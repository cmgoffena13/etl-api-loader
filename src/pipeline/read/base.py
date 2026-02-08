from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

import structlog
from sqlalchemy.orm import Session, sessionmaker

from src.pipeline.read.authentication.factory import AuthenticationStrategyFactory
from src.pipeline.read.pagination.factory import PaginationStrategyFactory
from src.process.client import AsyncProductionHTTPClient
from src.settings import config
from src.sources.base import APIConfig, APIEndpointConfig

logger = structlog.getLogger(__name__)


class BaseReader(ABC):
    def __init__(
        self,
        source: APIConfig,
        client: AsyncProductionHTTPClient,
        Session: sessionmaker[Session],
        source_name: str,
        endpoint_name: str,
        **kwargs,
    ):
        self.source = source
        self.client = client
        self.Session = Session
        self.source_name = source_name
        self.endpoint_name = endpoint_name
        self.batch_size = config.BATCH_SIZE
        self.authentication_strategy = AuthenticationStrategyFactory.create_strategy(
            self.source, **self.source.authentication_params
        )
        self.pagination_strategy = PaginationStrategyFactory.create_strategy(
            source=self.source,
            client=self.client,
            Session=self.Session,
            source_name=self.source_name,
            endpoint_name=self.endpoint_name,
            **kwargs,
        )

    @abstractmethod
    async def read(
        self, url: str, endpoint_config: APIEndpointConfig
    ) -> AsyncGenerator[list[dict], None]:
        pass
