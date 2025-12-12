from sqlalchemy import Engine

from src.pipeline.write.base import BaseWriter
from src.pipeline.write.postgresql import PostgreSQLWriter
from src.settings import config


class WriterFactory:
    _writers = {
        "postgresql": PostgreSQLWriter,
    }

    @classmethod
    def get_supported_writers(cls) -> list[type[BaseWriter]]:
        return list(cls._writers.keys())

    @classmethod
    def create_writer(cls, engine: Engine) -> BaseWriter:
        try:
            writer_class = cls._writers[config.DRIVERNAME]
            return writer_class(engine=engine)
        except KeyError:
            raise ValueError(
                f"Unsupported writer type: {config.DRIVERNAME}. Supported writers: {cls.get_supported_writers()}"
            )
