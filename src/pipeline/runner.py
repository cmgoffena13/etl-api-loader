from src.enum import HttpMethod
from src.pipeline.read.factory import ReaderFactory
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APISourceConfig


class PipelineRunner:
    def __init__(
        self,
        endpoint: str,
        method: HttpMethod,
        config: APISourceConfig,
        client: AsyncProductionHTTPClient,
    ):
        self.config = config
        self.base_url = config.base_url
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

    def run(self):
        pass
