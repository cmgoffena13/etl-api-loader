from src.sources.base import APIConfig, APIEndpointConfig, TableConfig
from src.sources.jsonplaceholder.models.posts import JSONPlaceholderPosts

JSONPLACEHOLDER_CONFIG = APIConfig(
    name="jsonplaceholder",
    base_url="https://jsonplaceholder.typicode.com/",
    type="rest",
    endpoints={
        "posts": APIEndpointConfig(
            json_entrypoint=None,
            tables=[
                TableConfig(data_model=JSONPlaceholderPosts),
            ],
        )
    },
)
