from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

import structlog

from src.pipeline.read.authentication.factory import AuthenticationStrategyFactory
from src.pipeline.read.pagination.factory import PaginationStrategyFactory
from src.process.client import AsyncProductionHTTPClient
from src.settings import config
from src.sources.base import APIConfig, APIEndpointConfig

logger = structlog.getLogger(__name__)


class BaseReader(ABC):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        self.source = source
        self.client = client
        self.batch_size = config.BATCH_SIZE
        self.authentication_strategy = AuthenticationStrategyFactory.create_strategy(
            self.source, **self.source.authentication_params
        )
        self.pagination_strategy = PaginationStrategyFactory.create_strategy(
            source=self.source, client=self.client
        )

    @abstractmethod
    async def read(
        self, url: str, endpoint_config: APIEndpointConfig
    ) -> AsyncGenerator[list[dict], None]:
        pass
