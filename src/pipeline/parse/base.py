from src.sources.base import APIEndpointConfig


class BaseParser:
    def __init__(self, endpoint_config: APIEndpointConfig):
        self.endpoint_config = endpoint_config

    def parse(self, data: list[dict]) -> list[dict]:
        pass
