from abc import ABC, abstractmethod
from typing import Type

import structlog
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from src.exception.base import AuditFailedError, GrainValidationError
from src.pipeline.db_utils import db_get_primary_keys
from src.sources.base import APIEndpointConfig
from src.utils import camel_to_snake, retry

logger = structlog.getLogger(__name__)


class BaseAuditor(ABC):
    def __init__(self, endpoint_config: APIEndpointConfig, engine: Engine):
        self.endpoint_config = endpoint_config
        self.table_configs = [table_config for table_config in endpoint_config.tables]
        self.Session: sessionmaker[Session] = sessionmaker(bind=engine)

    @abstractmethod
    def create_grain_validation_sql(self, primary_keys: list[str]) -> str:
        pass

    @retry()
    def _audit_grain(self, data_model: Type[SQLModel]):
        stage_table_name = f"stage_{camel_to_snake(data_model.__name__)}"
        primary_keys = db_get_primary_keys(data_model)
        grain_sql = self.create_grain_validation_sql(primary_keys)
        grain_sql = grain_sql.format(table=stage_table_name)
        with self.Session() as session:
            result = session.execute(text(grain_sql)).fetchone()
            if result._mapping["grain_unique"] == 0:
                logger.error(f"Grain {stage_table_name} is not unique")
                raise GrainValidationError(f"Grain {stage_table_name} is not unique")

    def audit_grain(self):
        for table_config in self.table_configs:
            self._audit_grain(table_config.data_model)

    @retry()
    def _audit_data(self, data_model: Type[SQLModel], audit_sql: str) -> None:
        failed_audits = []
        stage_table_name = f"stage_{camel_to_snake(data_model.__name__)}"
        with self.Session() as session:
            audit_sql = audit_sql.format(table=stage_table_name)
            result = session.execute(text(audit_sql)).fetchone()
            column_names = list(result._mapping.keys())
        for audit_name in column_names:
            value = result._mapping[audit_name]
            if value == 0:
                failed_audits.append(audit_name)
        if failed_audits:
            failed_audits_formatted = ", ".join(failed_audits)
            logger.error(
                f"Audits failed for table {stage_table_name}: {failed_audits_formatted}"
            )
            raise AuditFailedError(
                f"Audits failed for table {stage_table_name}: {failed_audits_formatted}"
            )

    def audit_data(self) -> None:
        for table_config in self.table_configs:
            if table_config.audit_query is None:
                continue
            self._audit_data(table_config.data_model, table_config.audit_query)
