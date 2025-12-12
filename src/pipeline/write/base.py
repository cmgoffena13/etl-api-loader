from abc import ABC, abstractmethod
from typing import Any, Dict

import structlog
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.settings import config
from src.sources.base import TableBatch

logger = structlog.getLogger(__name__)


class BaseWriter(ABC):
    def __init__(self, engine: Engine):
        self.batch_size = config.BATCH_SIZE
        self.Session: sessionmaker[Session] = sessionmaker(bind=engine)
        self.columns = {}

    def cache_columns(self, table_batches: list[TableBatch]) -> None:
        if not self.columns:
            for table_batch in table_batches:
                model_name = table_batch.data_model.__name__
                column_list = list(table_batch.data_model.model_fields.keys())
                column_list.append("etl_row_hash")
                self.columns[model_name] = column_list

    def create_stage_insert_sql(self, table_name: str, columns: list[str]) -> str:
        placeholders = ", ".join([f":{col}" for col in columns])
        return text(
            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        )

    def _convert_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Can override in subclasses to add custom conversion logic."""
        return record

    def _write_batch(self, table_batch: TableBatch) -> None:
        stage_table_name = table_batch.stage_table_name
        columns = self.columns[table_batch.data_model.__name__]
        insert_sql = self.create_stage_insert_sql(stage_table_name, columns)

        batch = [None] * self.batch_size
        batch_index = 0
        for record in table_batch.records:
            record = self._convert_record(record)
            batch[batch_index] = record
            batch_index += 1
            if batch_index == self.batch_size:
                with self.Session() as session:
                    try:
                        session.execute(insert_sql, batch)
                        session.commit()
                    except Exception as e:
                        logger.exception(f"Error inserting batch into stage table: {e}")
                        session.rollback()
                        raise e
                batch[:] = [None] * self.batch_size
                batch_index = 0
        if batch_index > 0:
            with self.Session() as session:
                try:
                    session.execute(insert_sql, batch[:batch_index])
                    session.commit()
                except Exception as e:
                    logger.exception(f"Error inserting batch into stage table: {e}")
                    session.rollback()
                    raise e

    def write(self, table_batches: list[TableBatch]) -> None:
        self.cache_columns(table_batches)
        for table_batch in table_batches:
            self._write_batch(table_batch)
