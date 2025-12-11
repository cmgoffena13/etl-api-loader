import re
from typing import Type

from sqlalchemy import (
    Column,
    DateTime,
    Engine,
    LargeBinary,
    MetaData,
    PrimaryKeyConstraint,
    Table,
)
from sqlmodel import SQLModel
from sqlmodel.main import get_sqlalchemy_type

from src.settings import DevConfig, config


def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def create_production_table(
    model: Type[SQLModel], engine: Engine, metadata: MetaData
) -> Table:
    table_name = camel_to_snake(model.__name__)
    columns = []
    table_kwargs = {}
    primary_keys = model.__table__.primary_key.columns.keys()
    for name, field in model.model_fields.items():
        sa_type = get_sqlalchemy_type(field)
        nullable = not field.is_required()
        sa_column = Column(name, sa_type, nullable=nullable)
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


def create_stage_table(
    model: Type[SQLModel], engine: Engine, metadata: MetaData
) -> Table:
    snake_name = camel_to_snake(model.__name__)
    table_name = f"stage_{snake_name}"
    columns = []
    for name, field in model.model_fields.items():
        sa_type = get_sqlalchemy_type(field)
        nullable = not field.is_required()
        sa_column = Column(name, sa_type, nullable=nullable)
        columns.append(sa_column)
    columns.append(Column("etl_row_hash", LargeBinary(16), nullable=False))

    table = Table(table_name, metadata, *columns)
    metadata.drop_all(engine, tables=[table])
    metadata.create_all(engine, tables=[table])
