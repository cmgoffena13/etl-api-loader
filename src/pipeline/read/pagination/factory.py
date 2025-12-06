from src.pipeline.read.pagination.base import BasePaginationStrategy
from src.pipeline.read.pagination.offset import OffsetPaginationStrategy
from src.sources.base import APIConfig


class PaginationStrategyFactory:
    _strategies = {"offset": OffsetPaginationStrategy}

    @classmethod
    def get_supported_strategies(cls) -> list[type[BasePaginationStrategy]]:
        return list(cls._strategies.keys())

    @classmethod
    def create_strategy(cls, source: APIConfig, **kwargs) -> BasePaginationStrategy:
        try:
            strategy = cls._strategies[source.pagination_strategy]
            return strategy(**kwargs)
        except KeyError:
            raise ValueError(
                f"Unsupported pagination strategy: {source.pagination_strategy}. Supported strategies: {cls.get_supported_strategies()}"
            )
