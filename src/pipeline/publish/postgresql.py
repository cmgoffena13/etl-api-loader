from typing import Type

from sqlalchemy import Engine
from sqlmodel import SQLModel

from src.pipeline.publish.base import BasePublisher
from src.sources.base import APIEndpointConfig


class PostgreSQLPublisher(BasePublisher):
    def __init__(self, engine: Engine, endpoint_config: APIEndpointConfig):
        super().__init__(engine, endpoint_config)

    def create_publish_sql(self, data_model: Type[SQLModel], now_iso: str) -> str:
        return super().create_publish_sql(data_model, now_iso)
