from typing import Dict

import structlog
import xxhash

logger = structlog.getLogger(__name__)


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
