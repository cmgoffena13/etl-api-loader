from collections.abc import AsyncGenerator

import structlog
from pydantic import TypeAdapter, ValidationError

from src.settings import config
from src.sources.base import APIEndpointConfig

logger = structlog.getLogger(__name__)


class Validator:
    def __init__(self, endpoint_config: APIEndpointConfig):
        self.endpoint_config = endpoint_config
        if not endpoint_config.tables:
            raise ValueError("At least one table config is required")
        self.adapter = TypeAdapter(endpoint_config.tables[0].data_model)
        self.batch_size = config.BATCH_SIZE

    async def validate(self, batch: list[dict]) -> AsyncGenerator[list[dict], None]:
        validated_batch = [None] * self.batch_size
        batch_index = 0
        for record in batch:
            try:
                validated_record = self.adapter.validate_python(record).model_dump()
                validated_batch[batch_index] = validated_record
                batch_index += 1
            except ValidationError as e:
                raise e

            if batch_index == self.batch_size:
                yield validated_batch
                validated_batch[:] = [None] * self.batch_size
                batch_index = 0
        if batch_index > 0:
            yield validated_batch[:batch_index]
