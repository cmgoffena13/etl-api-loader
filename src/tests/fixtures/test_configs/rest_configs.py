from src.sources.base import (
    APIConfig,
    APIEndpointConfig,
    CursorPaginationConfig,
    NextUrlPaginationConfig,
    OffsetPaginationConfig,
    TableConfig,
)
from src.tests.fixtures.test_models.rest_models import TestItem

TEST_REST_CONFIG_NO_PAGINATION = APIConfig(
    name="test_api_no_pagination",
    base_url="https://api.example.com/",
    type="rest",
    endpoints={
        "items": APIEndpointConfig(
            json_entrypoint="items",
            tables=[
                TableConfig(data_model=TestItem),
            ],
        )
    },
)

TEST_REST_CONFIG_WITH_OFFSET_PAGINATION = APIConfig(
    name="test_api_offset_pagination",
    base_url="https://api.example.com",
    type="rest",
    pagination_strategy="offset",
    pagination=OffsetPaginationConfig(
        offset_param="offset",
        limit_param="limit",
        start_offset=0,
        max_concurrent=2,
        offset=0,
        limit=5,
    ),
    endpoints={
        "items": APIEndpointConfig(
            json_entrypoint="items",
            tables=[
                TableConfig(data_model=TestItem),
            ],
        )
    },
)

TEST_REST_CONFIG_WITH_NEXT_URL_PAGINATION = APIConfig(
    name="test_api_next_url_pagination",
    base_url="https://api.example.com/",
    type="rest",
    pagination_strategy="next_url",
    pagination=NextUrlPaginationConfig(
        next_url_key="next_url",
    ),
    endpoints={
        "items": APIEndpointConfig(
            json_entrypoint="results",
            tables=[
                TableConfig(data_model=TestItem),
            ],
        )
    },
)

TEST_REST_CONFIG_WITH_CURSOR_PAGINATION = APIConfig(
    name="test_api_cursor_pagination",
    base_url="https://api.example.com",
    type="rest",
    json_entrypoint="data",
    pagination_strategy="cursor",
    pagination=CursorPaginationConfig(
        cursor_param="starting_after",
        next_cursor_key="data[-1].id",
        limit_param="limit",
        limit=5,
    ),
    endpoints={
        "items": APIEndpointConfig(
            json_entrypoint="data",
            tables=[
                TableConfig(data_model=TestItem),
            ],
        )
    },
)
