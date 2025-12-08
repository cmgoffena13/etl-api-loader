from collections.abc import AsyncGenerator

import structlog
from pydantic import TypeAdapter, ValidationError

from src.pipeline.transform.transformer import TableBatch
from src.sources.base import APIEndpointConfig

logger = structlog.getLogger(__name__)


class Validator:
    def __init__(self, endpoint_config: APIEndpointConfig):
        self.endpoint_config = endpoint_config
        if not endpoint_config.tables:
            raise ValueError("At least one table config is required")
        self.adapters: dict[str, TypeAdapter] = {}
        self.stage_to_target: dict[str, str] = {}

        for table_config in endpoint_config.tables:
            self.adapters[table_config.target_table_name] = TypeAdapter(
                table_config.data_model
            )
            self.stage_to_target[table_config.stage_table_name] = (
                table_config.target_table_name
            )

    async def validate(
        self, table_batches: list[TableBatch]
    ) -> AsyncGenerator[list[TableBatch], None]:
        for table_batch in table_batches:
            target_table_name = self.stage_to_target[table_batch.stage_table_name]
            adapter = self.adapters[target_table_name]

            for index, record in enumerate(table_batch.records):
                try:
                    validated_record = adapter.validate_python(record).model_dump()
                    table_batch.records[index] = validated_record
                except ValidationError as e:
                    raise e

        yield table_batches
