from typing import Dict, Type

import structlog
import xxhash
from sqlalchemy import inspect as sa_inspect
from sqlmodel import SQLModel

from src.settings import config

logger = structlog.getLogger(__name__)


def db_create_row_hash(
    record: Dict[str, str], sorted_keys: tuple[str, ...] | None = None
) -> bytes:
    string_items = {
        key: str(value) if value is not None else "" for key, value in record.items()
    }

    keys = sorted_keys or ()
    data_string = "|".join(string_items[key] for key in keys if key in string_items)

    return xxhash.xxh128(data_string.encode("utf-8")).digest()


def db_get_primary_keys(data_model: Type[SQLModel]) -> list[str]:
    mapper = sa_inspect(data_model)
    return [col.key for col in mapper.primary_key]


def db_create_duplicate_grain_examples_sql(
    primary_keys: list[str], limit: int = 5
) -> str:
    drivername = config.DRIVERNAME

    if drivername == "mssql":
        top_clause = f"SELECT TOP({limit})"
        bottom_clause = ""
    else:
        top_clause = "SELECT"
        bottom_clause = f"LIMIT {limit}"

    grain_cols = ", ".join(primary_keys)
    duplicate_sql = f"""
    {top_clause}
    {grain_cols},
    COUNT(*) as duplicate_count
    FROM {{table}}
    GROUP BY {grain_cols}
    HAVING COUNT(*) > 1
    {bottom_clause}
    """
    return duplicate_sql
