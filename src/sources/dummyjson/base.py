from src.sources.base import APIConfig, APIEndpointConfig, OffsetPaginationConfig
from src.sources.dummyjson.models.products import DummyJSONProduct

DUMMYJSON_CONFIG = APIConfig(
    base_url="https://dummyjson.com",
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
    endpoints=[
        APIEndpointConfig(
            endpoint="/products",
            json_entrypoint="products",
            data_model=DummyJSONProduct,
        )
    ],
)
