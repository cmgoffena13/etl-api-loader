from collections.abc import AsyncGenerator
from typing import Any, Optional

import httpx
import structlog
from httpx import Request
from sqlalchemy.orm import Session, sessionmaker

from src.pipeline.read.json_utils import extract_items
from src.pipeline.read.pagination.base import BasePaginationStrategy
from src.pipeline.watermark import get_watermark, set_watermark
from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig, CursorPaginationConfig

logger = structlog.getLogger(__name__)


def _step(current: Any, part: str) -> Optional[Any]:
    """Resolve one path part (key or array index like "data[-1]") from current."""
    result = None
    try:
        if "[" in part and part.endswith("]"):
            key_part, index_part = part.split("[", 1)
            index_part = index_part.rstrip("]")
            arr = current[key_part]
            if isinstance(arr, list):
                i = -1 if index_part == "-1" else int(index_part)
                result = arr[i]
        elif isinstance(current, dict) and part in current:
            result = current[part]
    except (KeyError, IndexError, ValueError, TypeError):
        pass
    return result


def _extract_next_value(data: dict, key: str) -> Optional[str]:
    """
    Extract next page token from response (supports key path and array indexing like data[-1].id).
    Accepts string or int from the API; returns string for use as query param (e.g. cursor or offset).
    """
    for part in key.split("."):
        data = _step(data, part)
    return str(data) if isinstance(data, (str, int)) else None


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
        self.initial_value = source.pagination.initial_value

    async def _fetch_cursor(
        self,
        request: Request,
        cursor: str | None,
        endpoint_config: APIEndpointConfig,
    ) -> dict | None:
        """Fetch a page using the provided cursor (or initial_value when cursor is None)."""
        params = dict(request.url.params)
        token = cursor if cursor is not None else self.initial_value
        if token:
            params[self.cursor_param] = token
        params[self.limit_param] = self.limit
        url = str(request.url.copy_with(query=None))
        logger.debug(f"Fetching paginated page, url: {url}, cursor: {cursor}")
        try:
            return await self.client.get(
                url=url,
                backoff_starting_delay=endpoint_config.backoff_starting_delay,
                headers=request.headers,
                params=params,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                logger.debug(
                    f"400 Bad Request - stopping pagination, url: {e.request.url}, cursor: {cursor}"
                )
                return None
            raise

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
                next_cursor = _extract_next_value(response_data, self.next_cursor_key)
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

            next_cursor = _extract_next_value(response_data, self.next_cursor_key)
            if not next_cursor:
                logger.debug(
                    f"No next_cursor found in response - stopping pagination, cursor: {cursor}"
                )
                break

            cursor = next_cursor
            logger.debug(f"Using next_cursor from response, next_cursor: {next_cursor}")

        if endpoint_config.incremental and cursor:
            set_watermark(self.source_name, self.endpoint_name, cursor, self.Session)
