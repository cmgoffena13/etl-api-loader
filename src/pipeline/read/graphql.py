from collections.abc import AsyncGenerator

import structlog
from httpx import Request
from sqlalchemy.orm import Session, sessionmaker

from src.pipeline.read.base import BaseReader
from src.pipeline.read.json_utils import extract_items
from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig

logger = structlog.getLogger(__name__)


class GraphQLReader(BaseReader):
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

    async def read(
        self, url: str, endpoint_config: APIEndpointConfig
    ) -> AsyncGenerator[list[dict], None]:
        default_params = {
            **self.source.default_params,
            **endpoint_config.default_params,
        }
        request = Request(
            method="POST",
            json=endpoint_config.body,
            url=url,
            headers=self.source.default_headers,
            params=default_params,
        )
        if self.authentication_strategy is not None:
            request = self.authentication_strategy.apply(self.client, request)

        if self.pagination_strategy is not None:
            accumulated_items = []
            async for page_items in self.pagination_strategy.pages(
                request, endpoint_config
            ):
                accumulated_items.extend(page_items)
                while len(accumulated_items) >= self.batch_size:
                    batch = accumulated_items[: self.batch_size]
                    accumulated_items = accumulated_items[self.batch_size :]
                    logger.debug(f"Read batch of {len(batch)} items...")
                    yield batch
            if accumulated_items:
                logger.debug(f"Read final batch of {len(accumulated_items)} items")
                yield accumulated_items
        else:
            response = await self.client.post(
                url,
                backoff_starting_delay=endpoint_config.backoff_starting_delay,
                headers=dict(request.headers),
                params=default_params,
                json=endpoint_config.body,
            )
            response.raise_for_status()

            data = response.json()
            items = extract_items(data, endpoint_config, self.source)
            if items:
                logger.info(f"Read single batch of {len(items)} items")
                yield items
