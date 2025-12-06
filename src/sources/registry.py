from pydantic import BaseModel, Field

from src.enum import HttpMethod
from src.sources.base import APIConfig


class SourceRegistry(BaseModel):
    sources: list = Field(default_factory=list)

    def add_sources(self, sources: list) -> None:
        self.sources.extend(sources)

    def get_source(self, base_url: str, endpoint: str, method: HttpMethod) -> APIConfig:
        for source in self.sources:
            if source.base_url == base_url:
                for ep in source.endpoints:
                    if ep.endpoint == endpoint and ep.method == method:
                        return source
        raise ValueError(
            f"Source not found for base_url: {base_url}, endpoint: {endpoint}, method: {method}"
        )
