import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from typing import Optional

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
        self._thread_pool_shutdown = False
        self.thread_pool = None
        self.api_queue = Queue()
        self.results: list[tuple[bool, str, Optional[str]]] = []

    async def process_endpoint(self, name: str, endpoint: str):
        source = MASTER_SOURCE_REGISTRY.get_source(name)
        if endpoint not in source.endpoints:
            available = ", ".join(source.endpoints.keys())
            raise ValueError(
                f"Endpoint '{endpoint}' not found in source '{name}'. "
                f"Available endpoints: {available}"
            )
        endpoint_config = source.endpoints[endpoint]
        runner = PipelineRunner(
            source=source,
            endpoint=endpoint,
            endpoint_config=endpoint_config,
            client=self.client,
        )
        result = await runner.run()
        self.results.append(result)
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
            result = await runner.run()
            self.results.append(result)
        await self.close()

    def _worker(self):
        async def worker_loop():
            while True:
                try:
                    api = self.api_queue.get_nowait()
                    await self.process_api(api.name)
                    self.api_queue.task_done()
                except Empty:
                    break

        return asyncio.run(worker_loop())

    def process(self):
        self.thread_pool = ThreadPoolExecutor(
            max_workers=psutil.cpu_count(logical=False)
        )
        for source in MASTER_SOURCE_REGISTRY.get_all_sources():
            self.api_queue.put_nowait(source)

        try:
            futures = [
                self.thread_pool.submit(self._worker)
                for _ in range(self.thread_pool._max_workers)
            ]
            for future in futures:
                future.result()
        finally:
            if not self._thread_pool_shutdown:
                self.thread_pool.shutdown(wait=True)
                self._thread_pool_shutdown = True

    async def close(self):
        if not self._closed:
            await self.client.close()
            self._closed = True

    def __del__(self):
        if not self._thread_pool_shutdown and self.thread_pool:
            logger.warning("Processor thread pool not shut down before deletion")
            self.thread_pool.shutdown(wait=True)
            self._thread_pool_shutdown = True
        if not self._closed and self.client:
            logger.warning("Processor client not closed before deletion")
            self.client.close()
            self._closed = True
