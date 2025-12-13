from abc import ABC, abstractmethod
from typing import Type

import pendulum
import structlog
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from src.pipeline.db_utils import db_get_primary_keys
from src.sources.base import APIEndpointConfig
from src.utils import camel_to_snake, retry

logger = structlog.getLogger(__name__)


class BasePublisher(ABC):
    def __init__(self, engine: Engine, endpoint_config: APIEndpointConfig):
        self.engine = engine
        self.endpoint_config = endpoint_config
        self.Session: sessionmaker[Session] = sessionmaker(bind=self.engine)
        self.variable_cache = {}

    def cache_variables(self, data_model: Type[SQLModel], now_iso: str) -> None:
        if data_model.__name__ not in self.variable_cache:
            stage_table_name = f"stage_{camel_to_snake(data_model.__name__)}"
            target_table_name = camel_to_snake(data_model.__name__)
            primary_keys = db_get_primary_keys(data_model)
            columns = list(data_model.model_fields.keys())
            columns.append("etl_row_hash")
            insert_columns = columns + ["etl_created_at"]
            insert_values_list = [f"stage.{col}" for col in columns] + [f"'{now_iso}'"]
            update = [col for col in columns if col not in primary_keys]

            join_condition = f" AND ".join(
                [f"stage.{pk} = target.{pk}" for pk in primary_keys]
            )
            insert_columns_str = ", ".join(insert_columns)
            insert_values_str = ", ".join(insert_values_list)

            update_set = (
                ", ".join(f"{col} = stage.{col}" for col in update)
                + f", etl_updated_at = '{now_iso}'"
            )
            self.variable_cache[data_model.__name__] = {
                "stage_table_name": stage_table_name,
                "target_table_name": target_table_name,
                "primary_keys": primary_keys,
                "columns": columns,
                "insert_columns": insert_columns_str,
                "insert_values": insert_values_str,
                "update_set": update_set,
                "join_condition": join_condition,
            }

    @abstractmethod
    def create_publish_sql(self, data_model: Type[SQLModel], now_iso: str) -> str:
        variables = self.variable_cache[data_model.__name__]

        return text(f"""
            MERGE INTO {variables["target_table_name"]} AS target
            USING {variables["stage_table_name"]} AS stage
            ON {variables["join_condition"]}
            WHEN MATCHED AND stage.etl_row_hash != target.etl_row_hash THEN
                UPDATE SET {variables["update_set"]}
            WHEN NOT MATCHED THEN
                INSERT ({variables["insert_columns"]})
                VALUES ({variables["insert_values"]});
        """)

    @retry()
    def _publish(self, data_model: Type[SQLModel]):
        now_iso = pendulum.now("UTC").isoformat()
        self.cache_variables(data_model, now_iso)
        publish_sql = self.create_publish_sql(data_model, now_iso)
        stage_table_name = self.variable_cache[data_model.__name__]["stage_table_name"]
        target_table_name = self.variable_cache[data_model.__name__][
            "target_table_name"
        ]
        with self.Session() as session:
            logger.info(
                f"Publishing data from {stage_table_name} to {target_table_name}..."
            )
            try:
                session.execute(publish_sql)
                session.commit()
            except Exception as e:
                logger.exception(f"Error publishing data: {e}")
                session.rollback()
                raise e

    def publish(self):
        for table_config in self.endpoint_config.tables:
            self._publish(table_config.data_model)
