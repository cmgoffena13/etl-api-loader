from collections.abc import AsyncGenerator
from typing import Any

from src.sources.base import APIEndpointConfig, TableRelationship


class TableBatch:
    def __init__(self, table_name: str, records: list[dict[str, Any]]):
        self.table_name = table_name
        self.records = records


class Transformer:
    def __init__(self, endpoint_config: APIEndpointConfig):
        self.endpoint_config = endpoint_config
        self.tables = endpoint_config.tables

    async def transform(
        self, batch: list[dict[str, Any]]
    ) -> AsyncGenerator[list[TableBatch], None]:
        if not batch or not self.tables:
            return

        related_entrypoints = {
            table.json_entrypoint
            for table in self.tables
            if table.relationship is not None
        }

        for table_config in self.tables:
            table_records: list[dict[str, Any]] = []

            if table_config.relationship is None:
                for record in batch:
                    main_record = self._extract_main_record(record, related_entrypoints)
                    table_records.append(main_record)
            else:
                relationship = table_config.relationship
                parent_id_field = relationship.parent_id_field

                for record in batch:
                    parent_id = record.get(parent_id_field)
                    if parent_id is None:
                        continue

                    nested_data = record.get(table_config.json_entrypoint)
                    if not nested_data:
                        continue

                    if isinstance(nested_data, list):
                        for nested_item in nested_data:
                            if nested_item:
                                related_record = self._extract_related_record(
                                    nested_item,
                                    parent_id,
                                    relationship,
                                )
                                table_records.append(related_record)
                    else:
                        related_record = self._extract_related_record(
                            nested_data, parent_id, relationship
                        )
                        table_records.append(related_record)
            if table_records:
                yield [
                    TableBatch(
                        table_name=table_config.stage_table_name,
                        records=table_records,
                    )
                ]

    def _extract_main_record(
        self, record: dict[str, Any], related_entrypoints: set[str]
    ) -> dict[str, Any]:
        main_record = {}
        for key, value in record.items():
            if key in related_entrypoints:
                continue

            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    main_record[f"{key}_{nested_key}"] = nested_value
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                continue
            else:
                main_record[key] = value
        return main_record

    def _extract_related_record(
        self,
        nested_item: dict[str, Any] | str,
        parent_id: Any,
        relationship: TableRelationship,
    ) -> dict[str, Any]:
        if isinstance(nested_item, str):
            return {
                relationship.foreign_key_name: parent_id,
                "url": nested_item,
            }

        record = dict(nested_item)
        record[relationship.foreign_key_name] = parent_id
        return record
