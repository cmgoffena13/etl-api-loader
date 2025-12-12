from sqlalchemy import Engine

from src.pipeline.write.base import BaseWriter


class PostgreSQLWriter(BaseWriter):
    def __init__(self, engine: Engine):
        super().__init__(engine=engine)
