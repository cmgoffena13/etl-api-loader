import json
import re
from typing import Any, AsyncGenerator

from pydantic import TypeAdapter, ValidationError

from src.pipeline.db_utils import db_create_row_hash
from src.pipeline.parse.base import BaseParser
from src.sources.base import APIEndpointConfig, TableBatch


class JSONParser(BaseParser):
    def __init__(self, endpoint_config: APIEndpointConfig):
        super().__init__(endpoint_config)
        self.table_batches: dict[str, TableBatch] = {}
        self.model_adapters: dict[str, TypeAdapter] = {}
        self.errors = []
        self.indexed_cache = {}
        self.regex_pattern_cache = {}
        self.model_fields_cache = {}
        self.sorted_keys_cache = {}
        self.index_pattern = re.compile(r"\[(\d+)\]")
        self._initialized = False

    async def _initialize(self) -> None:
        if not self._initialized:
            await self._create_table_batches_and_adapters()
            self._initialized = True

    async def clear_index_cache(self):
        self.indexed_cache = {}

    async def _model_specs_find_deepest_common_path_pattern(
        self, aliases: list[str]
    ) -> str:
        paths = [".".join(alias.split(".")[:-1]) for alias in aliases]
        path_segments = [path.split(".") for path in paths]
        common_segments = []
        min_length = min(len(segments) for segments in path_segments)

        for index in range(min_length):
            segments_at_position = [segments[index] for segments in path_segments]
            first_segment = segments_at_position[0]
            first_base = (
                first_segment.split("[")[0] if "[" in first_segment else first_segment
            )

            if all(
                seg.split("[")[0] == first_base if "[" in seg else seg == first_base
                for seg in segments_at_position
            ):
                common_segments.append(first_segment)
            else:
                break

        return ".".join(common_segments) if common_segments else "root"

    async def _model_specs_find_deepest_wildcard_path(self, aliases: list[str]) -> str:
        return max(
            (".".join(alias.split(".")[:-1]) for alias in aliases),
            key=lambda p: p.count("."),
        )

    async def _create_table_batches_and_adapters(self) -> None:
        for model_cls in self.endpoint_config.tables:
            model_name = model_cls.__name__
            all_aliases = []
            fields = []
            sorted_keys = []

            for field_name, field_info in sorted(model_cls.model_fields.items()):
                alias = field_info.alias
                if alias is None:
                    raise ValueError(f"Alias is required for field {field_name}")

                has_wildcard = "[*]" in alias
                fields.append((field_name, alias, has_wildcard))
                all_aliases.append(alias)
                sorted_keys.append(field_name)

            self.model_fields_cache[model_name] = fields
            self.sorted_keys_cache[model_name] = tuple(sorted_keys)

            wildcard_aliases = [
                alias for _, alias, has_wildcard in fields if has_wildcard
            ]
            if wildcard_aliases:
                json_path_pattern = await self._model_specs_find_deepest_wildcard_path(
                    wildcard_aliases
                )
            else:
                json_path_pattern = (
                    await self._model_specs_find_deepest_common_path_pattern(
                        all_aliases
                    )
                )

            table_batch = TableBatch(
                data_model=model_cls,
                json_path_pattern=json_path_pattern,
            )

            self.table_batches[model_name] = table_batch
            self.model_adapters[model_name] = TypeAdapter(model_cls)

    async def _parsing_path_matches(self, path: str, pattern: str) -> bool:
        if pattern not in self.regex_pattern_cache:
            escaped = re.escape(pattern).replace(r"\[\*\]", r"\[\d+\]")
            self.regex_pattern_cache[pattern] = re.compile(escaped)
        return bool(self.regex_pattern_cache[pattern].fullmatch(path))

    async def _parsing_replace_wildcard_with_index(
        self, alias_path: str, current_path: str
    ) -> str:
        alias_segments = alias_path.split(".")
        current_segments = current_path.split(".")
        resolved_segments = []
        current_index = 0

        for alias_segment in alias_segments:
            if "[*]" in alias_segment:
                key_name = alias_segment.split("[")[0]
                found = False
                for index in range(current_index, len(current_segments)):
                    seg = current_segments[index]
                    if seg.startswith(key_name + "["):
                        match = self.index_pattern.search(seg)
                        if match:
                            resolved_segments.append(f"{key_name}[{match.group(1)}]")
                            current_index = index + 1
                            found = True
                            break
                if not found:
                    resolved_segments.append(alias_segment)
            else:
                resolved_segments.append(alias_segment)
                if (
                    current_index < len(current_segments)
                    and current_segments[current_index] == alias_segment
                ):
                    current_index += 1

        return ".".join(resolved_segments)

    async def _parsing_build_model_data(
        self, path: str, table_batch: TableBatch
    ) -> dict:
        data = {}
        model_name = table_batch.data_model.__name__
        for field_name, alias, has_wildcard in self.model_fields_cache[model_name]:
            if has_wildcard:
                list_path = alias.replace("[*]", "")
                list_value = self.indexed_cache.get(list_path)
                if isinstance(list_value, list):
                    if not list_value or not isinstance(list_value[0], dict):
                        data[field_name] = json.dumps(list_value)
                    else:
                        resolved_alias = (
                            await self._parsing_replace_wildcard_with_index(alias, path)
                        )
                        data[field_name] = self.indexed_cache.get(resolved_alias)
                else:
                    resolved_alias = await self._parsing_replace_wildcard_with_index(
                        alias, path
                    )
                    data[field_name] = self.indexed_cache.get(resolved_alias)
            else:
                resolved_alias = alias
                data[field_name] = self.indexed_cache.get(resolved_alias)
        return data

    async def _parsing_extract_models_at_path(self, path: str) -> None:
        for model_name, table_batch in self.table_batches.items():
            if await self._parsing_path_matches(path, table_batch.json_path_pattern):
                try:
                    data = await self._parsing_build_model_data(path, table_batch)
                    adapter = self.model_adapters[model_name]
                    sorted_keys = self.sorted_keys_cache[model_name]
                    record = adapter.validate_python(data).model_dump()
                    record["etl_row_hash"] = db_create_row_hash(record, sorted_keys)
                    table_batch.add_record(record)
                except ValidationError as e:
                    self.errors.append(
                        {
                            "path": path,
                            "model": model_name,
                            "errors": e.errors(),
                        }
                    )

    async def _parsing_walk(self, obj: Any, path: str = "root"):
        self.indexed_cache[path] = obj

        if isinstance(obj, dict):
            for key, value in obj.items():
                field_path = f"{path}.{key}"
                self.indexed_cache[field_path] = value
                if isinstance(value, (dict, list)):
                    await self._parsing_walk(value, field_path)

            await self._parsing_extract_models_at_path(path)

        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                item_path = f"{path}[{index}]"
                self.indexed_cache[item_path] = item
                if isinstance(item, (dict, list)):
                    await self._parsing_walk(item, item_path)

    async def parse(self, batch: list[dict]) -> AsyncGenerator[list[TableBatch], None]:
        await self._initialize()
        for table_batch in self.table_batches.values():
            table_batch.clear_records()
        await self.clear_index_cache()
        for record in batch:
            await self._parsing_walk(record)
        if self.errors:
            raise ValueError(self.errors)
        yield list(self.table_batches.values())
