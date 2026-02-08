from typing import Any, Literal, Optional, Type

from pydantic import BaseModel, Field, model_validator
from sqlmodel import SQLModel

from src.utils import camel_to_snake


class TableBatch:
    def __init__(
        self,
        data_model: Type[SQLModel],
        json_path_pattern: str,
    ):
        self.data_model = data_model
        self._records = []
        self.json_path_pattern = json_path_pattern
        self._stage_table_name = f"stage_{camel_to_snake(data_model.__name__)}"
        self._target_table_name = camel_to_snake(data_model.__name__)

    def add_record(self, record: dict):
        self._records.append(record)

    def clear_records(self):
        self._records = []

    @property
    def records(self):
        return self._records

    @property
    def stage_table_name(self):
        return self._stage_table_name

    @property
    def target_table_name(self):
        return self._target_table_name


class PaginationConfig(BaseModel):
    pass


class OffsetPaginationConfig(PaginationConfig):
    offset_param: str = Field(default="offset")
    limit_param: str = Field(default="limit")
    start_offset: int = Field(default=0)
    max_concurrent: int = Field(default=5)
    offset: int
    limit: int


class CursorPaginationConfig(PaginationConfig):
    cursor_param: str = Field(default="cursor")
    next_cursor_key: str = Field(default="next_cursor")
    limit_param: str = Field(default="limit")
    limit: int = Field(default=100)

    """Optional value for the first request when no cursor/watermark (e.g. '0' for offset-style)."""
    initial_value: Optional[str] = Field(default=None)


class NextUrlPaginationConfig(PaginationConfig):
    next_url_key: str = Field(default="next_url")


class TableConfig(BaseModel):
    data_model: Type[SQLModel]
    audit_query: Optional[str] = None


class APIEndpointConfig(BaseModel):
    json_entrypoint: Optional[str] = None
    body: Optional[dict[str, Any]] = None
    default_params: dict[str, Any] = Field(default_factory=dict)
    backoff_starting_delay: float = Field(default=1)
    incremental: bool = Field(default=False)
    tables: list[TableConfig]


class APIConfig(BaseModel):
    name: str
    base_url: str
    type: Literal["rest", "graphql"]
    parse_type: Literal["json"] = Field(default="json")
    json_entrypoint: Optional[str] = None
    default_headers: dict[str, str] = Field(default_factory=dict)
    default_params: dict[str, Any] = Field(default_factory=dict)

    pagination_strategy: Optional[Literal["offset", "next_url", "cursor"]] = None
    pagination: Optional[PaginationConfig] = None

    authentication_strategy: Optional[Literal["auth", "bearer"]] = None
    authentication_params: dict[str, Any] = Field(default_factory=dict)

    endpoints: dict[str, APIEndpointConfig]

    @model_validator(mode="after")
    def validate_pagination_config(self):
        if (self.pagination_strategy is not None and self.pagination is None) or (
            self.pagination_strategy is None and self.pagination is not None
        ):
            raise ValueError(
                "pagination must be provided when pagination_strategy is set and vice versa"
            )
        return self

    @model_validator(mode="after")
    def validate_authentication_params(self):
        if (
            self.authentication_strategy is not None
            and self.authentication_params == {}
        ) or (
            self.authentication_strategy is None and self.authentication_params != {}
        ):
            raise ValueError(
                "authentication_params must be provided when authentication_strategy is set and vice versa"
            )
        return self
