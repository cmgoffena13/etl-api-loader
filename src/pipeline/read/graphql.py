from collections.abc import AsyncGenerator

from src.pipeline.read.base import BaseReader
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig


class GraphQLReader(BaseReader):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        super().__init__(source=source, client=client)

    async def read(self, endpoint: str) -> AsyncGenerator[list[dict], None]:
        pass
