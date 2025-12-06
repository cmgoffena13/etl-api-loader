from abc import ABC, abstractmethod
from typing import Any

from src.pipeline.read.authentication.factory import AuthenticationStrategyFactory
from src.pipeline.read.pagination.factory import PaginationStrategyFactory
from src.settings import config
from src.sources.base import APIConfig


class BaseReader(ABC):
    def __init__(self, source: APIConfig):
        self.source = source
        self.batch_size = config.BATCH_SIZE
        self.authentication_strategy = AuthenticationStrategyFactory.create_strategy(
            source=source
        )
        self.pagination_strategy = PaginationStrategyFactory.create_strategy(
            source=source
        )

    @abstractmethod
    def read(self) -> Any:
        pass
