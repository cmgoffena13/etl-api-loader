from typing import Any

from src.enum import HttpMethod
from src.pipeline.read.base import BaseReader
from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig


class GraphQLReader(BaseReader):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        super().__init__(source=source, client=client)

    def read(self, endpoint: str, method: HttpMethod) -> Any:
        pass
