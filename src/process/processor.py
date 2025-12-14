import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from typing import Optional

import psutil
import structlog
from opentelemetry import trace

from src.pipeline.runner import PipelineRunner
from src.process.create_table import create_production_tables
from src.process.db import setup_db
from src.sources.base import APIConfig
from src.sources.master import MASTER_SOURCE_REGISTRY

logger = structlog.getLogger(__name__)

tracer = trace.get_tracer(__name__)


class Processor:
    def __init__(self):
        self.engine, self.metadata = setup_db()
        self._thread_pool_shutdown = False
        self.thread_pool = None
        self.api_queue = Queue()
        self.results: list[tuple[bool, str, Optional[str]]] = []
        logger.info("Processor Initialized")

    async def process_endpoint(
        self, name: str, endpoint: str, api_config: APIConfig = None
    ) -> None:
        source = (
            api_config
            if api_config is not None
            else MASTER_SOURCE_REGISTRY.get_source(name)
        )
        if endpoint not in source.endpoints:
            available = ", ".join(source.endpoints.keys())
            raise ValueError(
                f"Endpoint '{endpoint}' not found in source '{name}'. "
                f"Available endpoints: {available}"
            )
        endpoint_config = source.endpoints[endpoint]
        create_production_tables(endpoint_config, self.engine, self.metadata)

        with tracer.start_as_current_span(f"API: {name} - Endpoint: {endpoint}"):
            runner = PipelineRunner(
                source=source,
                endpoint=endpoint,
                endpoint_config=endpoint_config,
                engine=self.engine,
                metadata=self.metadata,
            )
            result = await runner.run()
            self.results.append(result)

    async def process_api(self, name: str) -> None:
        source = MASTER_SOURCE_REGISTRY.get_source(name)
        # Process Sequentially to respect API rate-limits
        for endpoint in source.endpoints.keys():
            await self.process_endpoint(name, endpoint, source)

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

    def process(self) -> None:
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

    def __del__(self):
        if hasattr(self, "_thread_pool_shutdown") and hasattr(self, "thread_pool"):
            if not self._thread_pool_shutdown and self.thread_pool:
                logger.warning("Processor thread pool not shut down before deletion")
                self.thread_pool.shutdown(wait=True)
                self._thread_pool_shutdown = True
