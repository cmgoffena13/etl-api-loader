from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from httpx import Request

from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig


class BasePaginationStrategy(ABC):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        self.source = source
        self.client = client

    @abstractmethod
    async def pages(
        self,
        request: Request,
        endpoint_config: APIEndpointConfig,
    ) -> AsyncGenerator[list[dict], None]:
        pass
