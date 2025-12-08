import asyncio
from collections.abc import AsyncGenerator
from typing import Optional
from urllib.parse import urljoin

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.pipeline.read.factory import ReaderFactory
from src.pipeline.transform.transformer import TableBatch, Transformer
from src.pipeline.validate.validator import Validator
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig

logger = structlog.getLogger(__name__)


class PipelineRunner:
    def __init__(
        self,
        source: APIConfig,
        endpoint: str,
        endpoint_config: APIEndpointConfig,
        client: AsyncProductionHTTPClient,
    ):
        clear_contextvars()
        bind_contextvars(source=source, endpoint=endpoint)
        self.source = source
        self.endpoint = endpoint.lstrip("/")
        self.endpoint_config = endpoint_config
        base_url = source.base_url.rstrip("/") + "/"
        self.url = urljoin(base_url, self.endpoint.lstrip("/"))
        self.client = client
        self.reader = ReaderFactory.create_reader(source=source, client=client)
        self.validator = Validator(endpoint_config=endpoint_config)
        self.transformer = Transformer(endpoint_config=endpoint_config)
        self.result: Optional[tuple[bool, str, Optional[str]]] = None

    async def read(self) -> AsyncGenerator[list[dict], None]:
        async for batch in self.reader.read(
            url=self.url, endpoint_config=self.endpoint_config
        ):
            yield batch

    async def transform(
        self, batch: list[dict]
    ) -> AsyncGenerator[list[TableBatch], None]:
        async for table_batches in self.transformer.transform(batch=batch):
            yield table_batches

    async def validate(
        self, table_batches: list[TableBatch]
    ) -> AsyncGenerator[list[dict], None]:
        async for validated_table_batches in self.validator.validate(
            table_batches=table_batches
        ):
            yield validated_table_batches

    def write(self, table_batches: list[TableBatch]) -> None:
        pass

    def audit(self) -> None:
        pass

    def publish(self) -> None:
        pass

    async def run(self):
        try:
            async for batch in self.read():
                print(batch[0])
                async for table_batches in self.transform(batch=batch):
                    async for validated_table_batches in self.validate(
                        table_batches=table_batches
                    ):
                        await asyncio.to_thread(self.write, validated_table_batches)
            await asyncio.to_thread(self.audit)
            await asyncio.to_thread(self.publish)
            self.result = (True, self.url, None)
        except Exception as e:
            logger.exception(e)
            self.result = (False, self.url, str(e))
        return self.result
