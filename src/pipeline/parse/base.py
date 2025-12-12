from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from src.sources.base import APIEndpointConfig, TableBatch


class BaseParser(ABC):
    def __init__(self, endpoint_config: APIEndpointConfig):
        self.endpoint_config = endpoint_config

    @abstractmethod
    async def parse(self, batch: list[dict]) -> AsyncGenerator[list[TableBatch], None]:
        pass
