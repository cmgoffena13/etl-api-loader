from typing import Dict, Type

import xxhash
from sqlalchemy import Engine
from sqlmodel import Field, SQLModel


def db_create_row_hash(
    record: Dict[str, str], sorted_keys: tuple[str, ...] | None = None
) -> bytes:
    string_items = {
        key: str(value) if value is not None else "" for key, value in record.items()
    }

    data_string = "|".join(
        string_items[key] for key in sorted_keys if key in string_items
    )

    return xxhash.xxh128(data_string.encode("utf-8")).digest()


def create_stage_table(
    model: Type[SQLModel], stage_table_name: str, engine: Engine
) -> Type[SQLModel]:
    fields = {}
    annotations = {}
    for field_name, field_info in model.model_fields.items():
        field_type = field_info.annotation
        field_kwargs = {}
        if field_info.default is not ...:
            field_kwargs["default"] = field_info.default
        if field_info.default_factory:
            field_kwargs["default_factory"] = field_info.default_factory

        # Explicitly set primary_key=False (or omit it) to remove primary key constraint
        # Don't include primary_key in field_kwargs since we want to remove it
        fields[field_name] = Field(**field_kwargs)
        annotations[field_name] = field_type

    # Add etl_row_hash field
    fields["etl_row_hash"] = Field(default="")
    annotations["etl_row_hash"] = str

    # Create the new model class dynamically
    # SQLModel will automatically create a table if __tablename__ is set
    stage_model = type(
        f"{model.__name__}Stage",
        (SQLModel,),
        {
            "__annotations__": annotations,
            **fields,
            "__tablename__": stage_table_name,
        },
    )

    # Ensure the class is properly initialized as a SQLModel table
    # SQLModel's __init_subclass__ should handle this, but we need to trigger it
    # by accessing the registry or creating the table definition
    if not hasattr(stage_model, "__table__"):
        # Force SQLModel to create the table definition
        stage_model.__init_subclass__()

    # Create the table in the database using SQLModel's metadata
    SQLModel.metadata.create_all(engine, tables=[stage_model.__table__])

    return stage_model
