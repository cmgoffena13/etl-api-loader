import asyncio
from collections.abc import AsyncGenerator
from urllib.parse import urlencode, urljoin

import structlog
from httpx import Request
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.pipeline.read.pagination.base import BasePaginationStrategy
from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig, QueryPaginationConfig

logger = structlog.getLogger(__name__)


class QueryPaginationStrategy(BasePaginationStrategy):
    """Pages through query result rows; each row → one GET (path or params from row)."""

    def __init__(
        self,
        source: APIConfig,
        client: AsyncProductionHTTPClient,
        Session: sessionmaker[Session],
        source_name: str,
        endpoint_name: str,
        *,
        engine: Engine,
    ):
        super().__init__(
            source=source,
            client=client,
            Session=Session,
            source_name=source_name,
            endpoint_name=endpoint_name,
        )
        self.client = client
        self.engine = engine
        if not isinstance(source.pagination, QueryPaginationConfig):
            raise ValueError(
                f"Expected QueryPaginationConfig, got {type(source.pagination)}"
            )
        self.config = source.pagination
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent)

    def _run_query(self) -> list[dict]:
        with self.engine.connect() as conn:
            result = conn.execute(text(self.config.query))
            return [dict(row) for row in result.mappings().fetchall()]

    def _url_for_row(self, base: str, row: dict) -> str:
        if self.config.value_in == "path":
            path = self.endpoint_name.format(**row)
            base_dir = base if base.endswith("/") else f"{base}/"
            url = urljoin(base_dir, path)
        else:
            qs = urlencode(row)
            url = f"{base}?{qs}"
        return url

    async def _fetch_one(
        self,
        url: str,
        request: Request,
        endpoint_config: APIEndpointConfig,
    ) -> dict:
        async with self.semaphore:
            return await self.client.get(
                url,
                backoff_starting_delay=endpoint_config.backoff_starting_delay,
                headers=dict(request.headers),
            )

    async def pages(
        self,
        request: Request,
        endpoint_config: APIEndpointConfig,
    ) -> AsyncGenerator[list[dict], None]:
        rows = self._run_query()
        if not rows:
            logger.warning("QueryPagination query returned no rows")
            return
        base = str(request.url).split("?")[0]
        logger.info(
            f"Query pagination: {len(rows)} rows, max_concurrent={self.config.max_concurrent}"
        )
        for index in range(0, len(rows), self.config.max_concurrent):
            chunk = rows[index : index + self.config.max_concurrent]
            tasks = [
                self._fetch_one(
                    self._url_for_row(base, row),
                    request,
                    endpoint_config,
                )
                for row in chunk
            ]
            results = await asyncio.gather(*tasks)
            yield list(results)
