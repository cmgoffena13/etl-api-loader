import asyncio
from collections.abc import AsyncGenerator
from typing import Optional
from urllib.parse import urljoin

import structlog
from sqlalchemy import Engine, MetaData
from sqlalchemy.orm import Session, sessionmaker
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.pipeline.audit.factory import AuditorFactory
from src.pipeline.parse.factory import ParserFactory
from src.pipeline.publish.factory import PublisherFactory
from src.pipeline.read.factory import ReaderFactory
from src.pipeline.watermark import commit_watermark
from src.pipeline.write.factory import WriterFactory
from src.process.client import AsyncProductionHTTPClient
from src.process.tables import create_stage_tables, drop_stage_tables
from src.sources.base import APIConfig, APIEndpointConfig, TableBatch

logger = structlog.getLogger(__name__)


class PipelineRunner:
    def __init__(
        self,
        source: APIConfig,
        endpoint: str,
        endpoint_config: APIEndpointConfig,
        engine: Engine,
        metadata: MetaData,
    ):
        clear_contextvars()
        bind_contextvars(source=source, endpoint=endpoint)
        self.source = source
        self.engine = engine
        self.metadata = metadata
        create_stage_tables(endpoint_config, self.engine, self.metadata)
        self.Session: sessionmaker[Session] = sessionmaker(bind=self.engine)
        self.endpoint = endpoint.lstrip("/")
        self.endpoint_config = endpoint_config

        if source.type == "graphql":
            self.url = source.base_url
        else:
            base_url = source.base_url.rstrip("/") + "/"
            self.url = urljoin(base_url, self.endpoint.lstrip("/"))

        self.client = AsyncProductionHTTPClient()
        self._client_closed = False
        self.reader = ReaderFactory.create_reader(
            source=source,
            client=self.client,
            Session=self.Session,
            source_name=source.name,
            endpoint_name=self.endpoint,
        )
        self.parser = ParserFactory.create_parser(
            source=source, endpoint_config=endpoint_config
        )
        self.writer = WriterFactory.create_writer(engine=self.engine)
        self.auditor = AuditorFactory.create_auditor(
            endpoint_config=endpoint_config, engine=self.engine
        )
        self.publisher = PublisherFactory.create_publisher(
            engine=self.engine, endpoint_config=endpoint_config
        )
        self.result: Optional[tuple[bool, str, Optional[str]]] = None

    async def read(self) -> AsyncGenerator[list[dict], None]:
        async for batch in self.reader.read(
            url=self.url, endpoint_config=self.endpoint_config
        ):
            yield batch

    async def parse(self, batch: list[dict]) -> AsyncGenerator[list[TableBatch], None]:
        async for table_batches in self.parser.parse(batch=batch):
            yield table_batches

    def write(self, table_batches: list[TableBatch]) -> None:
        self.writer.write(table_batches=table_batches)

    def audit(self) -> None:
        self.auditor.audit_grain()
        self.auditor.audit_data()

    def publish(self) -> None:
        self.publisher.publish()
        if self.endpoint_config.incremental:
            commit_watermark(self.source.name, self.endpoint, self.Session)

    def cleanup(self) -> None:
        drop_stage_tables(self.endpoint_config, self.Session)

    async def run(self):
        try:
            async for batch in self.read():
                async for table_batches in self.parse(batch=batch):
                    await asyncio.to_thread(self.write, table_batches)
            await asyncio.to_thread(self.audit)
            await asyncio.to_thread(self.publish)
            await asyncio.to_thread(self.cleanup)
            self.result = (True, self.url, None)
            logger.info(f"API Endpoint {self.url} processed successfully!")
        except Exception as e:
            logger.exception(f"Error processing endpoint {self.url}: {e}")
            self.result = (False, self.url, str(e))
        finally:
            if not self._client_closed:
                await self.client.close()
                self._client_closed = True
        return self.result
