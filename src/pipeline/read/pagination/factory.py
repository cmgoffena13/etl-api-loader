from typing import Optional

import structlog
from sqlalchemy.orm import Session, sessionmaker

from src.pipeline.read.pagination.base import BasePaginationStrategy
from src.pipeline.read.pagination.cursor import CursorPaginationStrategy
from src.pipeline.read.pagination.next_url import NextURLPaginationStrategy
from src.pipeline.read.pagination.offset import OffsetPaginationStrategy
from src.pipeline.read.pagination.query import QueryPaginationStrategy
from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig

logger = structlog.getLogger(__name__)


class PaginationStrategyFactory:
    _strategies = {
        "offset": OffsetPaginationStrategy,
        "next_url": NextURLPaginationStrategy,
        "cursor": CursorPaginationStrategy,
        "query": QueryPaginationStrategy,
    }

    @classmethod
    def get_supported_strategies(cls) -> list[type[BasePaginationStrategy]]:
        return list(cls._strategies.keys())

    @classmethod
    def create_strategy(
        cls,
        source: APIConfig,
        client: AsyncProductionHTTPClient,
        Session: sessionmaker[Session],
        source_name: str,
        endpoint_name: str,
        **kwargs,
    ) -> Optional[BasePaginationStrategy]:
        if source.pagination_strategy is None:
            return None
        try:
            logger.info(
                f"Creating pagination strategy: {source.pagination_strategy}",
                source=source_name,
                endpoint=endpoint_name,
            )
            strategy = cls._strategies[source.pagination_strategy]
            return strategy(
                source=source,
                client=client,
                Session=Session,
                source_name=source_name,
                endpoint_name=endpoint_name,
                **kwargs,
            )
        except KeyError:
            raise ValueError(
                f"Unsupported pagination strategy: {source.pagination_strategy}. Supported strategies: {cls.get_supported_strategies()}"
            )
