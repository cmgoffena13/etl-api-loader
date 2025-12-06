from src.pipeline.runner import PipelineRunner
from src.processor.client import AsyncProductionHTTPClient
from src.sources.master import MASTER_SOURCE_REGISTRY


class Processor:
    def __init__(self):
        self.client = AsyncProductionHTTPClient()

    def process(self, base_url: str, endpoint: str):
        source = MASTER_SOURCE_REGISTRY.get_source(base_url, endpoint)
        runner = PipelineRunner(base_url, endpoint, source, self.client)
        runner.run()
        self.close()

    def close(self):
        self.client.close()

    def __del__(self):
        if self.client:
            self.close()
