from src.sources.base import APIConfig, APIEndpointConfig, OffsetPaginationConfig
from src.tests.fixtures.test_models.rest_models import TestItem

TEST_REST_CONFIG_NO_PAGINATION = APIConfig(
    base_url="https://api.example.com",
    type="rest",
    endpoints=[
        APIEndpointConfig(
            endpoint="/items",
            data_model=TestItem,
        )
    ],
)

TEST_REST_CONFIG_WITH_OFFSET_PAGINATION = APIConfig(
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
    endpoints=[
        APIEndpointConfig(
            endpoint="/items",
            data_model=TestItem,
        )
    ],
)
