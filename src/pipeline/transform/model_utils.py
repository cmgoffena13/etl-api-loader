from typing import Type

from pydantic import BaseModel


async def get_api_field_names(model: Type[BaseModel]) -> set[str]:
    api_field_names = set()

    for field_name, field_info in model.model_fields.items():
        api_field_names.add(field_name)
        if field_info.alias:
            api_field_names.add(field_info.alias)
    return api_field_names


async def get_field_name_mapping(model: Type[BaseModel]) -> dict[str, str]:
    mapping = {}

    for field_name, field_info in model.model_fields.items():
        mapping[field_name] = field_name
        if field_info.alias:
            mapping[field_info.alias] = field_name
    return mapping
