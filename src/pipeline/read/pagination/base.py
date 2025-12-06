from abc import ABC, abstractmethod
from typing import Any, Callable

from src.processor.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig


class BasePaginationStrategy(ABC):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        self.source = source
        self.client = client

    @abstractmethod
    def paginate(self, query_function: Callable, *args) -> Any:
        pass
