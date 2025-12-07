from pydantic import BaseModel, Field

from src.sources.base import APIConfig


class SourceRegistry(BaseModel):
    sources: list = Field(default_factory=list)

    def add_sources(self, sources: list) -> None:
        self.sources.extend(sources)

    def get_source(self, name: str) -> APIConfig:
        for source in self.sources:
            if source.name == name:
                return source

        raise ValueError(f"Source not found for name: {name}")

    def get_all_sources(self) -> list[APIConfig]:
        return self.sources
