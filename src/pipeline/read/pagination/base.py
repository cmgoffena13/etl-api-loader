from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from httpx import Request
from sqlalchemy.orm import Session, sessionmaker

from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig, APIEndpointConfig


class BasePaginationStrategy(ABC):
    def __init__(
        self,
        source: APIConfig,
        client: AsyncProductionHTTPClient,
        Session: sessionmaker[Session],
        source_name: str,
        endpoint_name: str,
    ):
        self.source = source
        self.client = client
        self.Session = Session
        self.source_name = source_name
        self.endpoint_name = endpoint_name

    @abstractmethod
    async def pages(
        self,
        request: Request,
        endpoint_config: APIEndpointConfig,
    ) -> AsyncGenerator[list[dict], None]:
        pass
