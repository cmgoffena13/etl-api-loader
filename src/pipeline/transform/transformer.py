from collections.abc import AsyncGenerator
from typing import Any, Type

from pydantic import BaseModel

from src.pipeline.transform.model_utils import get_api_field_names
from src.sources.base import APIEndpointConfig, TableRelationship


class TableBatch:
    def __init__(
        self,
        stage_table_name: str,
        data_model: Type[BaseModel],
        records: list[dict[str, Any]],
    ):
        self.stage_table_name = stage_table_name
        self.data_model = data_model
        self.records = records


class Transformer:
    def __init__(self, endpoint_config: APIEndpointConfig):
        self.tables = endpoint_config.tables

    async def transform(
        self, batch: list[dict[str, Any]]
    ) -> AsyncGenerator[list[TableBatch], None]:
        related_entrypoints = {
            table.json_entrypoint
            for table in self.tables
            if table.relationship is not None
        }

        all_table_batches: list[TableBatch] = []

        for table_config in self.tables:
            table_records: list[dict[str, Any]] = []

            if table_config.relationship is None:
                for record in batch:
                    main_record = await self._extract_main_record(
                        record, table_config, related_entrypoints
                    )
                    table_records.append(main_record)
            else:
                relationship = table_config.relationship
                parent_id_field = relationship.parent_id_field

                for record in batch:
                    parent_id = record[parent_id_field]
                    nested_data = record[table_config.json_entrypoint]
                    if isinstance(nested_data, list):
                        for nested_item in nested_data:
                            related_record = await self._extract_related_record(
                                nested_item,
                                parent_id,
                                relationship,
                            )
                            table_records.append(related_record)
                    else:
                        related_record = await self._extract_related_record(
                            nested_data, parent_id, relationship
                        )
                        table_records.append(related_record)

            if table_records:
                all_table_batches.append(
                    TableBatch(
                        stage_table_name=table_config.stage_table_name,
                        data_model=table_config.data_model,
                        records=table_records,
                    )
                )

        if all_table_batches:
            yield all_table_batches

    async def _extract_main_record(
        self,
        record: dict[str, Any],
        table_config,
        related_entrypoints: set[str],
    ) -> dict[str, Any]:
        api_field_names = await get_api_field_names(table_config.data_model)

        main_record = {}
        for key, value in record.items():
            if key in related_entrypoints:
                continue
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    flattened_key = f"{key}_{nested_key}"
                    if flattened_key in api_field_names:
                        main_record[flattened_key] = nested_value
            elif isinstance(value, list):
                # Skip lists of dicts
                if value and isinstance(value[0], dict):
                    continue
                if key in api_field_names:
                    main_record[key] = value
            else:
                if key in api_field_names:
                    main_record[key] = value
        return main_record

    async def _extract_related_record(
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
