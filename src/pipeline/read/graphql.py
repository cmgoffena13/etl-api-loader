from collections.abc import AsyncGenerator

from httpx import Request

from src.pipeline.read.base import BaseReader
from src.pipeline.read.json_utils import extract_items
from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig


class GraphQLReader(BaseReader):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        super().__init__(source=source, client=client)

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
            async for page_items in self.pagination_strategy.pages(
                request, endpoint_config
            ):
                for batch in self._batch_items(page_items):
                    yield batch
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
            for batch in self._batch_items(items):
                yield batch
