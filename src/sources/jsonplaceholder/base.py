from src.sources.base import APIConfig, APIEndpointConfig
from src.sources.jsonplaceholder.models.posts import JSONPlaceholderPost

JSONPLACEHOLDER_CONFIG = APIConfig(
    base_url="https://jsonplaceholder.typicode.com",
    type="rest",
    endpoints=[
        APIEndpointConfig(
            endpoint="/posts",
            data_model=JSONPlaceholderPost,
        )
    ],
)
