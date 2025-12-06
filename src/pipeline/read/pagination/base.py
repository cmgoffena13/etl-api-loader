from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from httpx import Request

from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig


class BasePaginationStrategy(ABC):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        self.source = source
        self.client = client

    @abstractmethod
    async def pages(self, request: Request) -> AsyncGenerator[list[dict], None]:
        pass
