from typing import Any

from src.pipeline.reader.base import BaseReader
from src.sources.base import APIConfig


class RESTReader(BaseReader):
    def __init__(self, source: APIConfig):
        super().__init__(source=source)

    def read(self) -> Any:
        pass
