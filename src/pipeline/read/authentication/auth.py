from base64 import b64encode

from httpx import Request

from src.pipeline.read.authentication.base import BaseAuthenticationStrategy
from src.process.client import AsyncProductionHTTPClient


class AuthAuthenticationStrategy(BaseAuthenticationStrategy):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def apply(self, client: AsyncProductionHTTPClient, request: Request) -> Request:
        token = b64encode(f"{self.username}:{self.password}".encode()).decode("ascii")
        request.headers["Authorization"] = f"Basic {token}"
        return request
