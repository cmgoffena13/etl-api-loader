from abc import ABC, abstractmethod
from typing import Any


class BaseWriter(ABC):
    @abstractmethod
    def write(self, data: list[dict[str, Any]]) -> None:
        pass
