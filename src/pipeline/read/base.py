from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

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

    def _batch_items(self, items, endpoint_config):
        batch = [None] * self.batch_size
        batch_index = 0
        for item in items:
            if endpoint_config.json_entrypoint is not None:
                item = item[endpoint_config.json_entrypoint]
            batch[batch_index] = item
            batch_index += 1
            if batch_index == self.batch_size:
                yield batch
                batch[:] = [None] * self.batch_size
                batch_index = 0
        if batch_index > 0:
            yield batch[:batch_index]

    @abstractmethod
    async def read(self, endpoint: str) -> AsyncGenerator[list[dict], None]:
        pass
