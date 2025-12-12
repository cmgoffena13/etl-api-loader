from sqlalchemy import Engine

from src.pipeline.audit.base import BaseAuditor
from src.sources.base import APIEndpointConfig


class PostgreSQLAuditor(BaseAuditor):
    def __init__(self, endpoint_config: APIEndpointConfig, engine: Engine):
        super().__init__(endpoint_config=endpoint_config, engine=engine)

    def create_grain_validation_sql(self, primary_keys: list[str]):
        grain_sql = None
        if len(primary_keys) == 1:
            grain_sql = f"SELECT CASE WHEN COUNT(DISTINCT {primary_keys[0]}) = COUNT(*) THEN 1 ELSE 0 END AS grain_unique FROM {{table}}"
        else:
            grain_cols = ", ".join(primary_keys)
            grain_sql = f"SELECT CASE WHEN COUNT(DISTINCT ({grain_cols})) = COUNT(*) THEN 1 ELSE 0 END AS grain_unique FROM {{table}}"
        return grain_sql
