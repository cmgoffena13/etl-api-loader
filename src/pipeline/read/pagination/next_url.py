from collections.abc import AsyncGenerator

import httpx
import structlog
from httpx import Request

from src.pipeline.read.json_utils import extract_items
from src.pipeline.read.pagination.base import BasePaginationStrategy
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig, NextUrlPaginationConfig

logger = structlog.getLogger(__name__)


class NextURLPaginationStrategy(BasePaginationStrategy):
    def __init__(
        self,
        source: APIConfig,
        client: AsyncProductionHTTPClient,
    ):
        super().__init__(source=source, client=client)
        self.client = client
        if not isinstance(source.pagination, NextUrlPaginationConfig):
            raise ValueError(
                f"Expected NextUrlPaginationConfig, got {type(source.pagination)}"
            )
        self.next_url_key = source.pagination.next_url_key

    async def _fetch_url(
        self, url: str, headers: dict, endpoint_config: APIEndpointConfig
    ) -> dict:
        """Fetch a page using the provided URL."""
        logger.debug("Fetching paginated page", url=url)
        try:
            response = await self.client.get(
                url=url,
                backoff_starting_delay=endpoint_config.backoff_starting_delay,
                headers=headers,
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
                    response_text=e.response.text[:200] if e.response.text else None,
                )
                return {}
            raise

        return response.json()

    async def pages(
        self,
        request: Request,
        endpoint_config: APIEndpointConfig,
    ) -> AsyncGenerator[list[dict], None]:
        """Paginate through pages using next_url from the response."""
        current_url = str(request.url)
        headers = dict(request.headers)

        while True:
            response_data = await self._fetch_url(
                url=current_url, headers=headers, endpoint_config=endpoint_config
            )

            if not response_data:
                break

            items = extract_items(response_data, endpoint_config)
            if len(items) == 0:
                break

            yield items

            next_url = response_data.get(self.next_url_key)
            if not next_url:
                logger.debug(
                    "No next_url found in response - stopping pagination",
                    current_url=current_url,
                )
                break

            current_url = next_url
            logger.debug("Using next_url from response", next_url=next_url)
