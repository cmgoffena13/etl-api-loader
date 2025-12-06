from abc import ABC, abstractmethod
from typing import Any

from src.sources.base import APIConfig


class BaseReader(ABC):
    def __init__(self, source: APIConfig):
        self.source = source

    @abstractmethod
    def read(self) -> Any:
        pass
