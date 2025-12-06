from httpx import Request

from src.pipeline.read.authentication.base import BaseAuthenticationStrategy
from src.processor.client import AsyncProductionHTTPClient


class BearerAuthenticationStrategy(BaseAuthenticationStrategy):
    def __init__(self, token: str):
        self.token = token

    def apply(self, client: AsyncProductionHTTPClient, request: Request) -> Request:
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request
