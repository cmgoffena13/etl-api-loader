from collections.abc import AsyncGenerator

import httpx

from src.pipeline.read.base import BaseReader
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig


class RESTReader(BaseReader):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        super().__init__(source=source, client=client)

    async def read(
        self, url: str, endpoint_config: APIEndpointConfig
    ) -> AsyncGenerator[list[dict], None]:
        request = httpx.Request(
            method="GET",
            url=url,
            headers=self.source.default_headers,
            params=endpoint_config.params,
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
            response = await self.client.get(
                url,
                headers=dict(request.headers),
                params=endpoint_config.params,
            )
            response.raise_for_status()

            data = response.json()
            if endpoint_config.json_entrypoint is not None:
                items = data[endpoint_config.json_entrypoint]
            else:
                items = data if isinstance(data, list) else [data]
            for batch in self._batch_items(items):
                yield batch
