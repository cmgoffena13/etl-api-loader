from src.sources.base import APIConfig, APIEndpointConfig, TableConfig
from src.sources.jsonplaceholder.models.posts import JSONPlaceholderPost

JSONPLACEHOLDER_CONFIG = APIConfig(
    name="jsonplaceholder",
    base_url="https://jsonplaceholder.typicode.com/",
    type="rest",
    endpoints={
        "posts": APIEndpointConfig(
            json_entrypoint=None,
            tables=[
                TableConfig(
                    data_model=JSONPlaceholderPost,
                    stage_table_name="stage_posts",
                    target_table_name="posts",
                    primary_keys=["id"],
                )
            ],
        )
    },
)
