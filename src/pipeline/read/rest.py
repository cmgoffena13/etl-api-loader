from collections.abc import AsyncGenerator

import httpx

from src.pipeline.read.base import BaseReader
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig


class RESTReader(BaseReader):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        super().__init__(source=source, client=client)

    def _batch_items(self, items):
        """Helper method to batch items and yield batches."""
        batch = [None] * self.batch_size
        batch_index = 0
        for item in items:
            batch[batch_index] = item
            batch_index += 1
            if batch_index == self.batch_size:
                yield batch
                batch[:] = [None] * self.batch_size
                batch_index = 0
        if batch_index > 0:
            yield batch[:batch_index]

    async def read(self, endpoint: str) -> AsyncGenerator[list[dict], None]:
        endpoint_config = next(
            ep for ep in self.source.endpoints if ep.endpoint == endpoint
        )
        url = f"{self.source.base_url}{endpoint_config.endpoint}"
        request = httpx.Request(
            method="GET",
            url=url,
            headers=self.source.default_headers,
            json=endpoint_config.body,
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
                json=endpoint_config.body,
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
