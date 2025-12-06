from typing import Any, Callable

from src.pipeline.read.pagination.base import BasePaginationStrategy


class OffsetPaginationStrategy(BasePaginationStrategy):
    def __init__(self, offset: int, limit: int):
        self.offset = offset
        self.limit = limit

    def paginate(self, query_function: Callable, *args) -> Any:
        pass
