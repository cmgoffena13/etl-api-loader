from src.sources.base import (
    APIConfig,
    APIEndpointConfig,
    NextUrlPaginationConfig,
    OffsetPaginationConfig,
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
                TestItem,
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
                TestItem,
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
                TestItem,
            ],
        )
    },
)
