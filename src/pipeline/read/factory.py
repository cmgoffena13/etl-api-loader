from src.pipeline.read.base import BaseReader
from src.pipeline.read.graphql import GraphQLReader
from src.pipeline.read.rest import RESTReader
from src.process.client import AsyncProductionHTTPClient
from src.sources.base import APIConfig


class ReaderFactory:
    _readers = {"rest": RESTReader, "graphql": GraphQLReader}

    @classmethod
    def get_supported_readers(cls) -> list[type[BaseReader]]:
        return list(cls._readers.keys())

    @classmethod
    def create_reader(
        cls, source: APIConfig, client: AsyncProductionHTTPClient
    ) -> BaseReader:
        try:
            reader_class = cls._readers[source.type]
            return reader_class(source=source, client=client)
        except KeyError:
            raise ValueError(
                f"Unsupported reader type: {source.type}. Supported types: {cls.get_supported_readers()}"
            )
