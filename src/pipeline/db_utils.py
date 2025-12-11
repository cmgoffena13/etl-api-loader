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


def create_table(
    model: Type[SQLModel], engine: Engine, is_stage: bool = True
) -> Type[SQLModel]:
    fields = {}
    annotations = {}

    table_name = f"stage_{model.__name__}" if is_stage else model.__name__
    for field_name, field_info in model.model_fields.items():
        field_type = field_info.annotation
        field_kwargs = {}
        if field_info.default is not ...:
            field_kwargs["default"] = field_info.default
        if field_info.default_factory:
            field_kwargs["default_factory"] = field_info.default_factory

        fields[field_name] = Field(**field_kwargs)
        annotations[field_name] = field_type

    # Add etl_row_hash field
    fields["etl_row_hash"] = Field()
    annotations["etl_row_hash"] = str

    model_cls = type(
        f"{model.__name__}Stage",
        (SQLModel,),
        {
            "__annotations__": annotations,
            **fields,
            "__tablename__": table_name,
        },
    )

    if not hasattr(model_cls, "__table__"):
        model_cls.__init_subclass__()

    SQLModel.metadata.create_all(engine, tables=[model_cls.__table__])

    return model_cls
