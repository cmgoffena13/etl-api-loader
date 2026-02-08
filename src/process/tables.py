from typing import Type, get_args

import structlog
from sqlalchemy import (
    Column,
    DateTime,
    Engine,
    LargeBinary,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    inspect,
    text,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel
from sqlmodel.main import get_sqlalchemy_type

from src.pipeline.db_utils import db_get_primary_keys
from src.settings import DevConfig, config
from src.sources.base import APIEndpointConfig
from src.utils import camel_to_snake, retry

logger = structlog.getLogger(__name__)


def _is_nullable(field) -> bool:
    return type(None) in get_args(field.annotation) or field.default is None


def _get_model_columns(model: Type[SQLModel]) -> dict[str, dict]:
    """Extract column information (type, nullable) from model fields."""
    columns = {}
    for name, field in model.model_fields.items():
        sa_type = get_sqlalchemy_type(field)
        if sa_type is DateTime:
            sa_type = DateTime(timezone=True)
        nullable = _is_nullable(field)
        columns[name] = {
            "type": sa_type,
            "nullable": nullable,
        }
    return columns


@retry()
def _create_production_table(
    model: Type[SQLModel], engine: Engine, metadata: MetaData
) -> Table:
    table_name = camel_to_snake(model.__name__)
    columns = []
    table_kwargs = {}
    primary_keys = db_get_primary_keys(model)
    model_columns = _get_model_columns(model)
    for name, col_info in model_columns.items():
        sa_column = Column(name, col_info["type"], nullable=col_info["nullable"])
        columns.append(sa_column)

    columns.append(Column("etl_row_hash", LargeBinary(16), nullable=False))
    columns.append(Column("etl_created_at", DateTime(timezone=True), nullable=False))
    columns.append(Column("etl_updated_at", DateTime(timezone=True), nullable=True))

    primary_key = PrimaryKeyConstraint(*primary_keys)

    if config.DRIVERNAME == "bigquery":
        table_kwargs["bigquery_clustering_fields"] = primary_keys

    table = Table(table_name, metadata, *columns, primary_key, **table_kwargs)
    if isinstance(config, DevConfig):
        metadata.drop_all(engine, tables=[table])
    metadata.create_all(engine, tables=[table])


def create_production_tables(
    endpoint_config: APIEndpointConfig, engine: Engine, metadata: MetaData
) -> None:
    for table_config in endpoint_config.tables:
        _create_production_table(table_config.data_model, engine, metadata)


@retry()
def _create_stage_table(
    model: Type[SQLModel], engine: Engine, metadata: MetaData
) -> Table:
    snake_name = camel_to_snake(model.__name__)
    table_name = f"stage_{snake_name}"
    columns = []
    model_columns = _get_model_columns(model)
    for name, col_info in model_columns.items():
        sa_column = Column(name, col_info["type"], nullable=col_info["nullable"])
        columns.append(sa_column)
    columns.append(Column("etl_row_hash", LargeBinary(16), nullable=False))

    table = Table(table_name, metadata, *columns)

    logger.debug(f"Creating stage table: {table_name}")
    metadata.drop_all(engine, tables=[table])
    metadata.create_all(engine, tables=[table])


def create_stage_tables(
    endpoint_config: APIEndpointConfig, engine: Engine, metadata: MetaData
) -> None:
    logger.info(f"Creating {len(endpoint_config.tables)} stage tables...")
    for table_config in endpoint_config.tables:
        _create_stage_table(table_config.data_model, engine, metadata)


@retry()
def _db_drop_stage_table(stage_table_name: str, Session: sessionmaker[Session]):
    with Session() as session:
        try:
            drop_sql = text(f"DROP TABLE IF EXISTS {stage_table_name}")
            session.execute(drop_sql)
            session.commit()
            logger.debug(f"Dropped stage table: {stage_table_name}")
        except Exception as e:
            logger.exception(f"Error dropping stage table: {stage_table_name}: {e}")
            session.rollback()
            raise e


def drop_stage_tables(
    endpoint_config: APIEndpointConfig, Session: sessionmaker[Session]
) -> None:
    stage_table_names = []
    for table_config in endpoint_config.tables:
        table_name = camel_to_snake(table_config.data_model.__name__)
        stage_table_names.append(f"stage_{table_name}")

    logger.info(f"Dropping {len(stage_table_names)} stage tables...")
    for stage_table_name in stage_table_names:
        _db_drop_stage_table(stage_table_name, Session)


@retry()
def create_watermark_table(engine: Engine, metadata: MetaData) -> None:
    watermark_table_name = "api_watermark"
    columns = [
        Column("source_name", String(255), nullable=False),
        Column("endpoint_name", String(255), nullable=False),
        Column("watermark_value", String(255), nullable=True),
        Column("watermark_attempted", String(255), nullable=True),
        Column("etl_created_at", DateTime(timezone=True), nullable=False),
        Column("etl_updated_at", DateTime(timezone=True), nullable=True),
    ]
    primary_key = PrimaryKeyConstraint("source_name", "endpoint_name")
    watermark_table = Table(watermark_table_name, metadata, *columns, primary_key)
    metadata.create_all(engine, tables=[watermark_table])


def evolve_table_schema(model: Type[SQLModel], engine: Engine) -> None:
    target_table_name = camel_to_snake(model.__name__)
    inspector = inspect(engine)

    model_columns = _get_model_columns(model)
    model_columns_keys = set(model_columns.keys())

    etl_columns = {"etl_row_hash", "etl_created_at", "etl_updated_at"}
    target_columns_keys = {
        col["name"]
        for col in inspector.get_columns(target_table_name)
        if col["name"] not in etl_columns
    }

    missing_columns = model_columns_keys - target_columns_keys

    if not missing_columns:
        logger.debug(f"No schema evolution needed for {target_table_name}")
        return

    logger.info(
        f"Evolving {target_table_name}: adding {len(missing_columns)} column(s): {', '.join(missing_columns)}"
    )

    drivername = engine.dialect.name
    add_column_keyword = "ADD COLUMN" if drivername != "mssql" else "ADD"

    with engine.begin() as conn:
        for col_name in missing_columns:
            col_info = model_columns[col_name]
            col_type = col_info["type"]
            type_str = col_type.compile(engine.dialect)
            nullable_str = "" if col_info["nullable"] else " NOT NULL"

            alter_sql = f"ALTER TABLE {target_table_name} {add_column_keyword} {col_name} {type_str}{nullable_str}"

            try:
                conn.execute(text(alter_sql))
                logger.debug(
                    f"Added column {col_name} ({type_str}) to {target_table_name}"
                )
            except Exception as e:
                logger.error(
                    f"Error adding column {col_name} to {target_table_name}: {e}"
                )
                raise
