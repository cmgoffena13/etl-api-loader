from collections.abc import AsyncGenerator

import httpx
import structlog
from httpx import Request
from sqlalchemy.orm import Session, sessionmaker

from src.pipeline.read.json_utils import extract_items
from src.pipeline.read.pagination.base import BasePaginationStrategy
from src.pipeline.watermark import get_watermark, set_watermark
from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig, NextUrlPaginationConfig

logger = structlog.getLogger(__name__)


def _get_nested_value(data: dict, key: str) -> str | None:
    keys = key.split(".")
    current = data
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current if isinstance(current, str) else None


class NextURLPaginationStrategy(BasePaginationStrategy):
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
        if not isinstance(source.pagination, NextUrlPaginationConfig):
            raise ValueError(
                f"Expected NextUrlPaginationConfig, got {type(source.pagination)}"
            )
        self.next_url_key = source.pagination.next_url_key

    async def _fetch_url(
        self, url: str, headers: dict, endpoint_config: APIEndpointConfig
    ) -> dict | None:
        """Fetch a page using the provided URL."""
        logger.debug(f"Fetching paginated page for url: {url}")
        try:
            return await self.client.get(
                url=url,
                backoff_starting_delay=endpoint_config.backoff_starting_delay,
                headers=headers,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                logger.debug(
                    f"400 Bad Request - stopping pagination, url: {e.request.url}"
                )
                return None
            raise

    async def pages(
        self,
        request: Request,
        endpoint_config: APIEndpointConfig,
    ) -> AsyncGenerator[list[dict], None]:
        """Paginate through pages using next_url from the response."""
        headers = dict(request.headers)
        current_url = str(request.url)

        if endpoint_config.incremental:
            watermark = get_watermark(
                self.source_name, self.endpoint_name, self.Session
            )
            if watermark:
                logger.info(f"Using watermark to get next URL: {watermark}")
                response_data = await self._fetch_url(
                    url=watermark, headers=headers, endpoint_config=endpoint_config
                )
                next_url = _get_nested_value(response_data, self.next_url_key)
                if next_url:
                    current_url = next_url
                else:
                    logger.warning(
                        f"No new data starting from watermark {watermark} - stopping pagination"
                    )
                    return

        while True:
            response_data = await self._fetch_url(
                url=current_url, headers=headers, endpoint_config=endpoint_config
            )

            if not response_data:
                break

            items = extract_items(response_data, endpoint_config, self.source)
            if len(items) == 0:
                break

            yield items

            next_url = _get_nested_value(response_data, self.next_url_key)
            if not next_url:
                logger.debug(
                    f"No next_url found in response - stopping pagination: {current_url}",
                )
                if endpoint_config.incremental:
                    set_watermark(
                        self.source_name, self.endpoint_name, current_url, self.Session
                    )
                break

            current_url = next_url
            logger.debug(f"Using next_url from response: {next_url}")
