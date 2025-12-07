from concurrent.futures import ThreadPoolExecutor

import psutil
import structlog

from src.pipeline.runner import PipelineRunner
from src.processor.client import AsyncProductionHTTPClient
from src.sources.master import MASTER_SOURCE_REGISTRY

logger = structlog.getLogger(__name__)


class Processor:
    def __init__(self):
        self.client = AsyncProductionHTTPClient()
        self._closed = False
        self.thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=psutil.cpu_count(logical=False)
        )

    async def process_endpoint(self, name: str, endpoint: str):
        source = MASTER_SOURCE_REGISTRY.get_source(name)
        endpoint_config = source.endpoints[endpoint]
        runner = PipelineRunner(
            source=source,
            endpoint=endpoint,
            endpoint_config=endpoint_config,
            client=self.client,
        )
        await runner.run()
        await self.close()

    async def process_api(self, name: str):
        source = MASTER_SOURCE_REGISTRY.get_source(name)
        # Process Sequentially to respect API rate-limits
        for endpoint, endpoint_config in source.endpoints.items():
            runner = PipelineRunner(
                source=source,
                endpoint=endpoint,
                endpoint_config=endpoint_config,
                client=self.client,
            )
            await runner.run()

    async def close(self):
        if not self._closed:
            await self.client.close()
            self._closed = True

    def __del__(self):
        if not self._closed and self.client:
            logger.warning("Processor client not closed before deletion")
