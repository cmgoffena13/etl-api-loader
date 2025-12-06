from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from src.enum import HttpMethod
from src.pipeline.read.authentication.factory import AuthenticationStrategyFactory
from src.pipeline.read.pagination.factory import PaginationStrategyFactory
from src.processor.client import AsyncProductionHTTPClient
from src.settings import config
from src.sources.base import APIConfig


class BaseReader(ABC):
    def __init__(self, source: APIConfig, client: AsyncProductionHTTPClient):
        self.source = source
        self.client = client
        self.batch_size = config.BATCH_SIZE
        self.authentication_strategy = AuthenticationStrategyFactory.create_strategy(
            source=source
        )
        self.pagination_strategy = PaginationStrategyFactory.create_strategy(
            source=source, client=client
        )

    @abstractmethod
    async def read(
        self, endpoint: str, method: HttpMethod
    ) -> AsyncGenerator[list[dict], None]:
        pass
