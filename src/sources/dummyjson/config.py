from src.sources.base import (
    APIConfig,
    APIEndpointConfig,
    OffsetPaginationConfig,
)
from src.sources.dummyjson.models.products import DummyJSONProducts, DummyJSONReviews

DUMMYJSON_CONFIG = APIConfig(
    name="dummyjson",
    base_url="https://dummyjson.com/",
    type="rest",
    pagination_strategy="offset",
    pagination=OffsetPaginationConfig(
        offset_param="skip",
        limit_param="limit",
        start_offset=0,
        max_concurrent=5,
        offset=0,
        limit=10,
    ),
    endpoints={
        "products": APIEndpointConfig(
            json_entrypoint="products",
            tables=[
                DummyJSONProducts,
                DummyJSONReviews,
            ],
        )
    },
)
