from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from httpx import Request
from sqlalchemy import Engine
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
        engine: Engine,
    ):
        self.source = source
        self.client = client
        self.Session = Session
        self.source_name = source_name
        self.endpoint_name = endpoint_name
        self.engine = engine

    @abstractmethod
    async def pages(
        self,
        request: Request,
        endpoint_config: APIEndpointConfig,
    ) -> AsyncGenerator[list[dict], None]:
        if False:  # pragma: no cover
            yield []
        raise NotImplementedError
