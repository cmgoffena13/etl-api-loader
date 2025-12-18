from typing import Optional

from httpx import Request

from src.pipeline.read.authentication.base import BaseAuthenticationStrategy
from src.process.client import AsyncProductionHTTPClient


class AuthAuthenticationStrategy(BaseAuthenticationStrategy):
    def __init__(self, username: str, password: str):
        self.auth = (username, password)

    def apply(self, client: AsyncProductionHTTPClient, request: Request) -> Request:
        request.auth = self.auth
        return request
