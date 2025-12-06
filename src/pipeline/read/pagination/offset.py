import asyncio
from collections.abc import AsyncGenerator

from httpx import Request

from src.pipeline.read.pagination.base import BasePaginationStrategy
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig


class OffsetPaginationStrategy(BasePaginationStrategy):
    def __init__(
        self,
        source: APIConfig,
        client: AsyncProductionHTTPClient,
    ):
        super().__init__(source=source, client=client)
        self.client = client
        self.offset = source.pagination.offset
        self.limit = source.pagination.limit
        self.offset_param = source.pagination.offset_param
        self.limit_param = source.pagination.limit_param
        self.start_offset = source.pagination.start_offset
        self.max_concurrent = source.pagination.max_concurrent
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

    async def _fetch_offset(
        self,
        request: Request,
        offset: int,
    ) -> list[dict]:
        async with self.semaphore:
            request.params[self.offset_param] = offset
            request.params[self.limit_param] = self.limit
            method_function = getattr(self.client, request.method.lower())
            response = await method_function(url=request.url, params=request.params)
            response.raise_for_status()
            data = response.json()
            items = data if isinstance(data, list) else [data]
            return items

    async def pages(self, request: Request) -> AsyncGenerator[list[dict], None]:
        offset = self.start_offset

        while True:
            tasks = []
            for index in range(self.max_concurrent):
                current_offset = offset + (index * self.limit)
                tasks.append(
                    self._fetch_offset(
                        request=request,
                        offset=current_offset,
                    )
                )

            results = await asyncio.gather(*tasks)

            all_empty = True
            for items in results:
                if len(items) > 0:
                    all_empty = False
                    yield items
                else:
                    break
            if all_empty:
                break

            offset += self.max_concurrent * self.limit

            if any(len(items) < self.limit for items in results if len(items) > 0):
                break
