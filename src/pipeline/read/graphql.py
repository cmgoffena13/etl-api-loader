from typing import Any

from src.pipeline.read.base import BaseReader
from src.sources.base import APIConfig


class GraphQLReader(BaseReader):
    def __init__(self, source: APIConfig):
        super().__init__(source=source)

    def read(self) -> Any:
        pass
