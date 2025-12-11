from abc import ABC, abstractmethod

from httpx import Request

from src.process.client import AsyncProductionHTTPClient


class BaseAuthenticationStrategy(ABC):
    @abstractmethod
    def apply(self, client: AsyncProductionHTTPClient, request: Request) -> Request:
        pass
