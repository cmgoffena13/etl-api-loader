from sqlalchemy import Engine

from src.pipeline.audit.base import BaseAuditor
from src.pipeline.audit.postgresql import PostgreSQLAuditor
from src.settings import config
from src.sources.base import APIEndpointConfig


class AuditorFactory:
    _auditors = {
        "postgresql": PostgreSQLAuditor,
    }

    @classmethod
    def get_supported_auditors(cls) -> list[type[BaseAuditor]]:
        return list(cls._auditors.keys())

    @classmethod
    def create_auditor(
        cls, endpoint_config: APIEndpointConfig, engine: Engine
    ) -> BaseAuditor:
        try:
            auditor_class = cls._auditors[config.DRIVERNAME]
            return auditor_class(endpoint_config=endpoint_config, engine=engine)
        except KeyError:
            raise ValueError(
                f"Unsupported auditor type: {config.DRIVERNAME}. Supported auditors: {cls.get_supported_auditors()}"
            )
