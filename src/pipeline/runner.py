import asyncio
from typing import Optional
from urllib.parse import urljoin

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.pipeline.read.factory import ReaderFactory
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
        self.url = urljoin(base_url, self.endpoint)
        self.client = client
        self.reader = ReaderFactory.create_reader(source=source, client=client)
        self.validator = Validator(endpoint_config=endpoint_config)
        self.result: Optional[tuple[bool, str, Optional[str]]] = None

    async def read(self):
        async for batch in self.reader.read(
            url=self.url, endpoint_config=self.endpoint_config
        ):
            yield batch

    async def validate(self, batch: list[dict]):
        async for validated_batch in self.validator.validate(batch=batch):
            yield validated_batch

    def write(self):
        pass

    def audit(self):
        pass

    def publish(self):
        pass

    async def run(self):
        try:
            async for batch in self.read():
                async for validated_batch in self.validate(batch=batch):
                    await asyncio.to_thread(self.write, validated_batch)
                    print(validated_batch)
            await asyncio.to_thread(self.audit)
            await asyncio.to_thread(self.publish)
            self.result = (True, self.url, None)
        except Exception as e:
            logger.exception(e)
            self.result = (False, self.url, str(e))
        return self.result
