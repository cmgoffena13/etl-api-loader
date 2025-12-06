from src.enum import HttpMethod
from src.pipeline.read.factory import ReaderFactory
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

    def read(self):
        return self.reader.read(endpoint=self.endpoint, method=self.method)

    def validate(self):
        pass

    def write(self):
        pass

    async def run(self):
        async for batch in self.read():
            print(batch)
