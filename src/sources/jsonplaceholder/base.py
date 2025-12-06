from src.enum import HttpMethod
from src.sources.base import APIConfig, APIEndpointConfig
from src.sources.jsonplaceholder.models.posts import JSONPlaceholderPost

JSONPLACEHOLDER_CONFIG = APIConfig(
    base_url="https://jsonplaceholder.typicode.com",
    type="rest",
    endpoints=[
        APIEndpointConfig(
            method=HttpMethod.GET,
            endpoint="/posts",
            data_model=JSONPlaceholderPost,
        )
    ],
)
