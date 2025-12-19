import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from typing import Optional

import psutil
import structlog
from opentelemetry import trace

from src.notify.factory import NotifierFactory
from src.notify.webhook import AlertLevel
from src.pipeline.runner import PipelineRunner
from src.process.create_table import create_production_tables, create_watermark_table
from src.process.db import setup_db
from src.sources.base import APIConfig
from src.sources.master import MASTER_SOURCE_REGISTRY

logger = structlog.getLogger(__name__)

tracer = trace.get_tracer(__name__)


class Processor:
    def __init__(self):
        self.engine, self.metadata = setup_db()
        create_watermark_table(self.engine, self.metadata)
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
            self.results_summary()
        finally:
            if not self._thread_pool_shutdown:
                self.thread_pool.shutdown(wait=True)
                self._thread_pool_shutdown = True

    def results_summary(self):
        success_count = 0
        failure_count = 0
        endpoints_failed = {}
        for result in self.results:
            status, url, error_message = result
            if status is True:
                success_count += 1
            elif status is False:
                failure_count += 1
                endpoints_failed[url] = error_message

        logger.info(
            f"Processing complete: {success_count} successful, {failure_count} failed"
        )

        if endpoints_failed:
            failure_details = "\n".join(
                f"• {endpoint_url}: {error_message}"
                for endpoint_url, error_message in endpoints_failed.items()
            )
            message = f"\n\nFailed Endpoints:\n{failure_details}"
            notifier = NotifierFactory.get_notifier("webhook")
            webhook_notifier = notifier(
                level=AlertLevel.ERROR,
                title="API Processing Summary",
                message=message,
            )
            webhook_notifier.notify()

    def __del__(self):
        if hasattr(self, "_thread_pool_shutdown") and hasattr(self, "thread_pool"):
            if not self._thread_pool_shutdown and self.thread_pool:
                logger.warning("Processor thread pool not shut down before deletion")
                self.thread_pool.shutdown(wait=True)
                self._thread_pool_shutdown = True
