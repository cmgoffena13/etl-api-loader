from src.enum import HttpMethod
from src.pipeline.runner import PipelineRunner
from src.processor.client import AsyncProductionHTTPClient
from src.sources.master import MASTER_SOURCE_REGISTRY


class Processor:
    def __init__(self):
        self.client = AsyncProductionHTTPClient()

    def process(self, base_url: str, endpoint: str, method: HttpMethod):
        source = MASTER_SOURCE_REGISTRY.get_source(base_url, endpoint, method)
        runner = PipelineRunner(
            endpoint=endpoint, method=method, config=source, client=self.client
        )
        runner.run()
        self.close()

    def close(self):
        self.client.close()

    def __del__(self):
        if self.client:
            self.close()
