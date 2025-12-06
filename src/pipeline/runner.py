from src.pipeline.read.factory import ReaderFactory
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APISourceConfig


class PipelineRunner:
    def __init__(
        self,
        base_url: str,
        endpoint: str,
        config: APISourceConfig,
        client: AsyncProductionHTTPClient,
    ):
        self.base_url = base_url
        self.endpoint = endpoint
        self.config = config
        self.client = client
        self.reader = ReaderFactory.create_reader(source=config, client=client)

    def read(self):
        yield from self.reader.read()

    def validate(self):
        pass

    def write(self):
        pass

    def run(self):
        pass
