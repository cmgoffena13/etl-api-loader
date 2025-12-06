from typing import Any, Literal, Type

from pydantic import BaseModel, ConfigDict, Field

from src.enum import HttpMethod


class APIEndpointConfig(BaseModel):
    method: HttpMethod = Field(default=HttpMethod.GET)
    endpoint: str
    params: dict[str, Any] = Field(default_factory=dict)
    data_model: Type[BaseModel]
    nested: list["APIEndpointConfig"] = Field(default_factory=list)
    extract_id: str = Field(default="id")

    model_config = ConfigDict(from_attributes=True)


class APIConfig(BaseModel):
    base_url: str
    type: Literal["rest", "graphql"]
    pagination_strategy: Literal["offset"] = None
    authentication_strategy: Literal["auth", "bearer"] = None
    default_headers: dict[str, str]
    pagination: dict[str, Any] = Field(default_factory=dict)
    endpoints: list[APIEndpointConfig] = Field(default_factory=list)
    nested_relations: dict[str, list[str]] = Field(default_factory=dict)
