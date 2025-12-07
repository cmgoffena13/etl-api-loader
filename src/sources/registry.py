from typing import Optional

from pydantic import BaseModel, Field

from src.sources.base import APIConfig


class SourceRegistry(BaseModel):
    sources: list = Field(default_factory=list)

    def add_sources(self, sources: list) -> None:
        self.sources.extend(sources)

    def get_source(
        self,
        base_url: str,
        endpoint: Optional[str] = None,
    ) -> APIConfig:
        sources = []
        for source in self.sources:
            if source.base_url == base_url:
                if endpoint is None:
                    sources.append(source)
                else:
                    for ep in source.endpoints:
                        if ep.endpoint == endpoint:
                            sources.append(source)
                            break
        if len(sources) == 0:
            raise ValueError(
                f"Source not found for base_url: {base_url}, endpoint: {endpoint}"
            )
        if len(sources) > 1:
            raise ValueError(
                f"Multiple sources found for base_url: {base_url}, endpoint: {endpoint}"
            )
        return sources[0]
