from typing import Optional

from pydantic import BaseModel, Field

from src.enum import HttpMethod
from src.sources.base import APIConfig


class SourceRegistry(BaseModel):
    sources: list = Field(default_factory=list)

    def add_sources(self, sources: list) -> None:
        self.sources.extend(sources)

    def get_source(
        self,
        base_url: str,
        endpoint: Optional[str] = None,
        method: Optional[HttpMethod] = None,
    ) -> APIConfig:
        sources = []
        for source in self.sources:
            if source.base_url == base_url:
                if endpoint is None and method is None:
                    sources.append(source)
                if endpoint is not None and method is not None:
                    for ep in source.endpoints:
                        if ep.endpoint == endpoint and ep.method == method:
                            sources.append(source)
        if len(sources) == 0:
            raise ValueError(
                f"Source not found for base_url: {base_url}, endpoint: {endpoint}, method: {method}"
            )
        if len(sources) > 1:
            raise ValueError(
                f"Multiple sources found for base_url: {base_url}, endpoint: {endpoint}, method: {method}"
            )
        return sources[0]
