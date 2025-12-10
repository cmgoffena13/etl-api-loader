from typing import Any, Literal, Optional, Type

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TableBatch:
    def __init__(
        self,
        stage_table_name: str,
        data_model: Type[BaseModel],
        json_path_pattern: str,
    ):
        self.stage_table_name = stage_table_name
        self.data_model = data_model
        self._records = []
        self.json_path_pattern = json_path_pattern

    def add_record(self, record: dict):
        self._records.append(record)

    def clear_records(self):
        self._records = []

    @property
    def records(self):
        return self._records


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


class NextUrlPaginationConfig(PaginationConfig):
    next_url_key: str = Field(default="next_url")


class TableRelationship(BaseModel):
    parent_id_field: str
    foreign_key_name: str


class TableConfig(BaseModel):
    data_model: Type[BaseModel]
    stage_table_name: str
    target_table_name: str
    json_entrypoint: Optional[str] = None
    relationship: Optional[TableRelationship] = None
    primary_keys: list[str]

    @model_validator(mode="after")
    def validate_primary_keys(self):
        model_fields = set(self.data_model.model_fields.keys())
        invalid_keys = [key for key in self.primary_keys if key not in model_fields]
        if invalid_keys:
            raise ValueError(
                f"Primary keys {invalid_keys} are not fields in model {self.data_model.__name__}. "
                f"Available fields: {sorted(model_fields)}"
            )
        return self


class APIEndpointConfig(BaseModel):
    json_entrypoint: Optional[str] = None
    body: Optional[dict[str, Any]] = None
    default_params: dict[str, Any] = Field(default_factory=dict)
    backoff_starting_delay: float = Field(default=1)
    tables: list[TableConfig]

    model_config = ConfigDict(from_attributes=True)


class APIConfig(BaseModel):
    name: str
    base_url: str
    type: Literal["rest", "graphql"]
    pagination_strategy: Optional[Literal["offset", "next_url"]] = None
    pagination: Optional[PaginationConfig] = None
    authentication_strategy: Optional[Literal["auth", "bearer"]] = None
    authentication_params: dict[str, Any] = Field(default_factory=dict)
    default_headers: dict[str, str] = Field(default_factory=dict)
    endpoints: dict[str, APIEndpointConfig] = Field(default_factory=dict)
    parse_type: Literal["json"] = Field(default="json")

    @model_validator(mode="after")
    def validate_pagination_config(self):
        if self.pagination_strategy is not None and self.pagination is None:
            raise ValueError(
                "pagination must be provided when pagination_strategy is set"
            )
        return self
