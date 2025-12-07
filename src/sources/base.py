from typing import Any, Literal, Optional, Type

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PaginationConfig(BaseModel):
    pass


class OffsetPaginationConfig(PaginationConfig):
    offset_param: str = Field(default="offset")
    limit_param: str = Field(default="limit")
    start_offset: int = Field(default=0)
    max_concurrent: int = Field(default=5)
    offset: int
    limit: int
    use_next_offset: bool = Field(default=False)
    next_offset_key: str = Field(default="next_offset")

    @model_validator(mode="after")
    def validate_next_offset_config(self):
        if self.use_next_offset and not self.next_offset_key:
            raise ValueError(
                "next_offset_key must be provided when use_next_offset is True"
            )
        return self


class APIEndpointConfig(BaseModel):
    endpoint: str
    json_entrypoint: Optional[str] = None
    body: Optional[dict[str, Any]] = None
    params: dict[str, Any] = Field(default_factory=dict)
    data_model: Type[BaseModel]
    nested: list["APIEndpointConfig"] = Field(default_factory=list)
    extract_id: str = Field(default="id")

    model_config = ConfigDict(from_attributes=True)


class APIConfig(BaseModel):
    base_url: str
    type: Literal["rest", "graphql"]
    pagination_strategy: Optional[Literal["offset"]] = None
    authentication_strategy: Optional[Literal["auth", "bearer"]] = None
    default_headers: dict[str, str] = Field(default_factory=dict)
    pagination: Optional[PaginationConfig] = None
    endpoints: list[APIEndpointConfig] = Field(default_factory=list)
    nested_relations: dict[str, list[str]] = Field(default_factory=dict)
