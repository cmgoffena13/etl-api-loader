from abc import ABC, abstractmethod
from typing import Any, Callable


class BasePaginationStrategy(ABC):
    @abstractmethod
    def paginate(self, query_function: Callable, *args) -> Any:
        pass
