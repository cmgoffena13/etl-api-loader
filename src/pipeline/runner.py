from urllib.parse import urljoin

import structlog

from src.pipeline.read.factory import ReaderFactory
from src.pipeline.validate.validator import Validator
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig

logger = structlog.getLogger(__name__)


class PipelineRunner:
    def __init__(
        self,
        endpoint: str,
        endpoint_config: APIEndpointConfig,
        config: APIConfig,
        client: AsyncProductionHTTPClient,
    ):
        self.config = config
        self.endpoint = endpoint.lstrip("/")
        base_url = config.base_url.rstrip("/") + "/"
        self.url = urljoin(base_url, self.endpoint)
        self.client = client
        self.reader = ReaderFactory.create_reader(source=config, client=client)
        endpoint_config = config.endpoints[self.endpoint]
        self.validator = Validator(endpoint_config=endpoint_config)

    async def read(self):
        async for batch in self.reader.read(endpoint=self.endpoint):
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
                    print(validated_batch)
        except Exception as e:
            logger.exception(e)
            raise e
