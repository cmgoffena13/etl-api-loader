from sqlalchemy import Engine

from src.pipeline.publish.base import BasePublisher
from src.pipeline.publish.postgresql import PostgreSQLPublisher
from src.settings import config
from src.sources.base import APIEndpointConfig


class PublisherFactory:
    _publishers = {
        "postgresql": PostgreSQLPublisher,
    }

    @classmethod
    def get_supported_publishers(cls) -> list[type[BasePublisher]]:
        return list(cls._publishers.keys())

    @classmethod
    def create_publisher(
        cls, engine: Engine, endpoint_config: APIEndpointConfig
    ) -> BasePublisher:
        try:
            publisher_class = cls._publishers[config.DRIVERNAME]
            return publisher_class(engine=engine, endpoint_config=endpoint_config)
        except KeyError:
            raise ValueError(
                f"Unsupported publisher type: {config.DRIVERNAME}. Supported publishers: {cls.get_supported_publishers()}"
            )
