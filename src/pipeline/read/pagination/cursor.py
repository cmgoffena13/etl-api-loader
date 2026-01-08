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
from src.sources.base import APIConfig, APIEndpointConfig, CursorPaginationConfig

logger = structlog.getLogger(__name__)


def _extract_cursor_value(data: dict, key: str) -> str | None:
    """Extract cursor value from response using key path (supports array indexing like data[-1].id)."""
    keys = key.split(".")
    current = data
    for k in keys:
        if k.endswith("]") and "[" in k:
            # Handle array indexing like "data[-1]"
            array_key, index_str = k.split("[")
            index_str = index_str.rstrip("]")
            if isinstance(current, dict) and array_key in current:
                arr = current[array_key]
                if isinstance(arr, list):
                    if index_str == "-1":
                        current = arr[-1] if len(arr) > 0 else None
                    else:
                        try:
                            idx = int(index_str)
                            current = arr[idx] if 0 <= idx < len(arr) else None
                        except ValueError:
                            return None
                    if current is None:
                        return None
                else:
                    return None
            else:
                return None
        elif isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current if isinstance(current, str) else None


class CursorPaginationStrategy(BasePaginationStrategy):
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
        if not isinstance(source.pagination, CursorPaginationConfig):
            raise ValueError(
                f"Expected CursorPaginationConfig, got {type(source.pagination)}"
            )
        self.cursor_param = source.pagination.cursor_param
        self.next_cursor_key = source.pagination.next_cursor_key
        self.limit_param = source.pagination.limit_param
        self.limit = source.pagination.limit

    async def _fetch_cursor(
        self,
        request: Request,
        cursor: str | None,
        endpoint_config: APIEndpointConfig,
    ) -> dict | None:
        """Fetch a page using the provided cursor."""
        params = dict(request.url.params)
        if cursor:
            params[self.cursor_param] = cursor
        params[self.limit_param] = self.limit
        method_function = getattr(self.client, request.method.lower())
        url = str(request.url.copy_with(query=None))
        logger.debug(f"Fetching paginated page, url: {url}, cursor: {cursor}")
        try:
            response = await method_function(
                url=url,
                backoff_starting_delay=endpoint_config.backoff_starting_delay,
                headers=request.headers,
                params=params,
            )
            logger.debug(
                f"Received response {response.status_code}",
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                logger.debug(
                    "400 Bad Request - stopping pagination, url: {str(e.request.url)}, cursor: {cursor}"
                )
                return None
            raise

        return orjson.loads(response.content)

    async def pages(
        self, request: Request, endpoint_config: APIEndpointConfig
    ) -> AsyncGenerator[list[dict], None]:
        """Paginate through pages using cursor from the response."""
        cursor = None
        if endpoint_config.incremental:
            watermark = get_watermark(
                self.source_name, self.endpoint_name, self.Session
            )
            if watermark:
                logger.info(f"Using watermark to get next cursor: {watermark}")
                response_data = await self._fetch_cursor(
                    request=request, cursor=watermark, endpoint_config=endpoint_config
                )
                next_cursor = _extract_cursor_value(response_data, self.next_cursor_key)
                if next_cursor:
                    cursor = next_cursor
                else:
                    logger.debug(
                        f"No new data starting from watermark {watermark} - stopping pagination"
                    )
                    return

        while True:
            response_data = await self._fetch_cursor(
                request=request, cursor=cursor, endpoint_config=endpoint_config
            )

            if not response_data:
                break

            items = extract_items(response_data, endpoint_config, self.source)
            if len(items) == 0:
                break

            yield items

            next_cursor = _extract_cursor_value(response_data, self.next_cursor_key)
            if not next_cursor:
                logger.debug(
                    f"No next_cursor found in response - stopping pagination, cursor: {cursor}"
                )
                break

            cursor = next_cursor
            logger.debug(f"Using next_cursor from response, next_cursor: {next_cursor}")

        if endpoint_config.incremental and cursor:
            set_watermark(self.source_name, self.endpoint_name, cursor, self.Session)
