import structlog

from src.enum import HttpMethod
from src.pipeline.runner import PipelineRunner
from src.processor.client import AsyncProductionHTTPClient
from src.sources.master import MASTER_SOURCE_REGISTRY

logger = structlog.getLogger(__name__)


class Processor:
    def __init__(self):
        self.client = AsyncProductionHTTPClient()

    async def process(self, base_url: str, endpoint: str, method: HttpMethod):
        source = MASTER_SOURCE_REGISTRY.get_source(base_url, endpoint, method)
        runner = PipelineRunner(
            endpoint=endpoint, method=method, config=source, client=self.client
        )
        await runner.run()
        await self.close()

    async def close(self):
        await self.client.close()

    def __del__(self):
        if self.client:
            logger.warning("Processor client not closed before deletion")
