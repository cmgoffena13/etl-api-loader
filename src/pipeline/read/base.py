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
        endpoint_config = source.endpoints[endpoint_name]
        effective_source = self._effective_source_for_pagination(
            source, endpoint_config
        )
        self.pagination_strategy = PaginationStrategyFactory.create_strategy(
            source=effective_source,
            client=self.client,
            Session=self.Session,
            source_name=self.source_name,
            endpoint_name=self.endpoint_name,
            **kwargs,
        )

    @staticmethod
    def _effective_source_for_pagination(
        source: APIConfig, endpoint_config: APIEndpointConfig
    ) -> APIConfig:
        """Use endpoint pagination when both set, else API-level."""
        if (
            endpoint_config.pagination_strategy is not None
            and endpoint_config.pagination is not None
        ):
            return source.model_copy(
                update={
                    "pagination_strategy": endpoint_config.pagination_strategy,
                    "pagination": endpoint_config.pagination,
                }
            )
        return source

    @abstractmethod
    async def read(
        self, url: str, endpoint_config: APIEndpointConfig
    ) -> AsyncGenerator[list[dict], None]:
        pass
