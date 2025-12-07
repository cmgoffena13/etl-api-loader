from src.enum import HttpMethod
from src.pipeline.read.factory import ReaderFactory
from src.pipeline.validate.validator import Validator
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig


class PipelineRunner:
    def __init__(
        self,
        endpoint: str,
        method: HttpMethod,
        config: APIConfig,
        client: AsyncProductionHTTPClient,
    ):
        self.config = config
        self.endpoint = endpoint
        self.method = method
        self.client = client
        self.reader = ReaderFactory.create_reader(source=config, client=client)
        self.validator = Validator(source=config)

    async def read(self):
        async for batch in self.reader.read(endpoint=self.endpoint, method=self.method):
            yield batch

    def validate(self, batch: list[dict]):
        self.validator.validate(batch=batch)

    def write(self):
        pass

    def audit(self):
        pass

    def publish(self):
        pass

    async def run(self):
        async for batch in self.read():
            self.validate(batch=batch)
