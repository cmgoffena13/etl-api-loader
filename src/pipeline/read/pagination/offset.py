import asyncio
from collections.abc import AsyncGenerator

import httpx
import structlog
from httpx import Request

from src.pipeline.read.pagination.base import BasePaginationStrategy
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig

logger = structlog.getLogger(__name__)


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
        self.use_next_offset = source.pagination.use_next_offset
        self.next_offset_key = source.pagination.next_offset_key
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

    def _extract_items(
        self, data: dict, endpoint_config: APIEndpointConfig
    ) -> list[dict]:
        if endpoint_config.json_entrypoint is not None:
            return data[endpoint_config.json_entrypoint]
        return data if isinstance(data, list) else [data]

    async def _fetch_offset(
        self,
        request: Request,
        offset: int,
    ) -> dict:
        async with self.semaphore:
            params = dict(request.url.params)
            params[self.offset_param] = offset
            params[self.limit_param] = self.limit
            method_function = getattr(self.client, request.method.lower())
            url = str(request.url.copy_with(query=None))
            logger.debug(
                "Fetching paginated page",
                url=url,
                method=request.method,
                params=params,
                offset=offset,
            )
            try:
                response = await method_function(
                    url=url,
                    headers=request.headers,
                    params=params,
                )
                logger.debug(
                    "Received response",
                    status_code=response.status_code,
                    url=str(response.url),
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.debug(
                        "400 Bad Request - stopping pagination",
                        url=str(e.request.url),
                        offset=offset,
                        response_text=e.response.text[:200]
                        if e.response.text
                        else None,
                    )
                    return {}
                raise

            return response.json()

    async def pages(
        self,
        request: Request,
        endpoint_config: APIEndpointConfig,
    ) -> AsyncGenerator[list[dict], None]:
        if self.use_next_offset:
            offset = self.start_offset
            while True:
                response_data = await self._fetch_offset(
                    request=request,
                    offset=offset,
                )

                if not response_data:
                    break

                items = self._extract_items(response_data, endpoint_config)
                if len(items) == 0:
                    break

                yield items

                next_offset = response_data.get(self.next_offset_key)
                if next_offset is None:
                    logger.debug(
                        "No next_offset found in response - stopping pagination",
                        offset=offset,
                    )
                    break

                offset = next_offset
                logger.debug(
                    "Using next_offset from response",
                    next_offset=next_offset,
                )
        else:
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
                for response_data in results:
                    if not response_data:
                        continue
                    items = self._extract_items(response_data, endpoint_config)
                    if len(items) > 0:
                        all_empty = False
                        yield items
                    else:
                        break
                if all_empty:
                    break

                offset += self.max_concurrent * self.limit

                has_partial_page = False
                for response_data in results:
                    if response_data:
                        items = self._extract_items(response_data, endpoint_config)
                        if len(items) > 0 and len(items) < self.limit:
                            has_partial_page = True
                            break
                if has_partial_page:
                    break
