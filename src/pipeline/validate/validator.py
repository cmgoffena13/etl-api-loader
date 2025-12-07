from collections.abc import AsyncGenerator

import structlog
from pydantic import TypeAdapter, ValidationError

from src.settings import config
from src.sources.base import APIConfig

logger = structlog.getLogger(__name__)


class Validator:
    def __init__(self, source: APIConfig):
        self.source = source
        self.adapter = TypeAdapter(self.source.data_model)
        self.batch_size = config.BATCH_SIZE

    def validate(self, batch: list[dict]) -> AsyncGenerator[list[dict], None]:
        batch = [None] * self.batch_size
        batch_index = 0
        for record in batch:
            try:
                record = self.adapter.validate_python(record).model_dump()
                batch[batch_index] = record
                batch_index += 1
            except ValidationError as e:
                raise e

            if batch_index == self.batch_size:
                yield batch
                batch[:] = [None] * self.batch_size
                batch_index = 0
        if batch_index > 0:
            yield batch[:batch_index]
