from httpx import Request

from src.pipeline.read.authentication.base import BaseAuthenticationStrategy
from src.processor.client import AsyncProductionHTTPClient


class AuthAuthenticationStrategy(BaseAuthenticationStrategy):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def apply(self, client: AsyncProductionHTTPClient, request: Request) -> Request:
        request.headers["Authorization"] = f"Basic {self.username}:{self.password}"
        return request
