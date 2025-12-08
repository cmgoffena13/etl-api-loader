from src.sources.base import (
    APIConfig,
    APIEndpointConfig,
    OffsetPaginationConfig,
    TableConfig,
    TableRelationship,
)
from src.sources.dummyjson.models.products import DummyJSONProduct, Review

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
                TableConfig(
                    data_model=DummyJSONProduct,
                    stage_table_name="stage_products",
                    target_table_name="products",
                ),
                TableConfig(
                    data_model=Review,
                    stage_table_name="stage_reviews",
                    target_table_name="reviews",
                    json_entrypoint="reviews",
                    relationship=TableRelationship(
                        parent_id_field="id",
                        foreign_key_name="product_id",
                    ),
                ),
            ],
        )
    },
)
