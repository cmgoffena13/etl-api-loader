import asyncio
from collections.abc import AsyncGenerator

import httpx
import orjson
import structlog
from httpx import Request
from sqlalchemy.orm import Session, sessionmaker

from src.pipeline.read.json_utils import extract_items
from src.pipeline.read.pagination.base import BasePaginationStrategy
from src.pipeline.watermark import get_watermark, set_watermark
from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig, OffsetPaginationConfig

logger = structlog.getLogger(__name__)


class OffsetPaginationStrategy(BasePaginationStrategy):
    def __init__(
        self,
        source: APIConfig,
        client: AsyncProductionHTTPClient,
        Session: sessionmaker[Session],
        source_name: str,
        endpoint_name: str,
    ):
        super().__init__(
            source=source,
            client=client,
            Session=Session,
            source_name=source_name,
            endpoint_name=endpoint_name,
        )
        self.client = client
        if not isinstance(source.pagination, OffsetPaginationConfig):
            raise ValueError(
                f"Expected OffsetPaginationConfig, got {type(source.pagination)}"
            )
        self.offset = source.pagination.offset
        self.limit = source.pagination.limit
        self.offset_param = source.pagination.offset_param
        self.limit_param = source.pagination.limit_param
        self.start_offset = source.pagination.start_offset
        self.max_concurrent = source.pagination.max_concurrent
        self.use_next_offset = source.pagination.use_next_offset
        self.next_offset_key = source.pagination.next_offset_key
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

    async def _fetch_offset(
        self,
        request: Request,
        offset: int,
        endpoint_config: APIEndpointConfig,
    ) -> dict | None:
        async with self.semaphore:
            params = dict(request.url.params)
            params[self.offset_param] = offset
            params[self.limit_param] = self.limit
            method_function = getattr(self.client, request.method.lower())
            url = str(request.url.copy_with(query=None))
            logger.debug(f"Fetching paginated page for url: {url}, offset: {offset}")
            try:
                response = await method_function(
                    url=url,
                    backoff_starting_delay=endpoint_config.backoff_starting_delay,
                    headers=request.headers,
                    params=params,
                )
                logger.debug(
                    f"Received response code: {response.status_code}",
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.debug(
                        f"400 Bad Request - stopping pagination, url: {str(e.request.url), offset: {offset}}",
                    )
                    return None
                raise

            return orjson.loads(response.content)

    async def pages(
        self,
        request: Request,
        endpoint_config: APIEndpointConfig,
    ) -> AsyncGenerator[list[dict], None]:
        offset = self.start_offset
        if endpoint_config.incremental:
            watermark = get_watermark(
                self.source_name, self.endpoint_name, self.Session
            )
            if watermark:
                try:
                    watermark_offset = int(watermark)
                except ValueError:
                    raise Exception(
                        f"Watermark value '{watermark}' is not a valid integer"
                    )
                logger.info(f"Using watermark to get next offset: {watermark_offset}")
                response_data = await self._fetch_offset(
                    request=request,
                    offset=watermark_offset,
                    endpoint_config=endpoint_config,
                )
                next_offset = response_data.get(self.next_offset_key)
                if next_offset:
                    offset = next_offset
                else:
                    logger.debug(
                        f"No new data starting from watermark {watermark} - stopping pagination"
                    )
                    return

        if self.use_next_offset:
            while True:
                response_data = await self._fetch_offset(
                    request=request,
                    offset=offset,
                    endpoint_config=endpoint_config,
                )

                if not response_data:
                    break

                items = extract_items(response_data, endpoint_config, self.source)
                if len(items) == 0:
                    break

                yield items

                next_offset = response_data.get(self.next_offset_key)
                if next_offset is None:
                    logger.debug(
                        f"No next_offset found in response - stopping pagination, offset: {offset}"
                    )
                    if endpoint_config.incremental:
                        set_watermark(
                            self.source_name,
                            self.endpoint_name,
                            str(next_offset),
                            self.Session,
                        )
                    break

                offset = next_offset
                logger.debug(f"Using next_offset from response: {next_offset}")
        else:
            highest_next_offset = offset
            while True:
                tasks = []
                for index in range(self.max_concurrent):
                    current_offset = offset + (index * self.limit)
                    tasks.append(
                        self._fetch_offset(
                            request=request,
                            offset=current_offset,
                            endpoint_config=endpoint_config,
                        )
                    )

                results = await asyncio.gather(*tasks)

                all_empty = True
                for index, response_data in enumerate(results):
                    if not response_data:
                        continue
                    items = extract_items(response_data, endpoint_config, self.source)
                    if len(items) > 0:
                        all_empty = False
                        request_offset = offset + (index * self.limit)
                        next_offset = request_offset + len(items)
                        highest_next_offset = max(highest_next_offset, next_offset)
                        yield items
                if all_empty:
                    break

                offset += self.max_concurrent * self.limit

                has_partial_page = False
                for response_data in results:
                    if response_data:
                        items = extract_items(
                            response_data, endpoint_config, self.source
                        )
                        if len(items) > 0 and len(items) < self.limit:
                            has_partial_page = True
                            break
                if has_partial_page:
                    break

            if endpoint_config.incremental:
                set_watermark(
                    self.source_name,
                    self.endpoint_name,
                    str(highest_next_offset),
                    self.Session,
                )
