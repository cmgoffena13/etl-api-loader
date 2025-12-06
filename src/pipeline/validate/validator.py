from src.sources.base import APIConfig


class Validator:
    def __init__(self, source: APIConfig):
        self.source = source

    def validate(self, data: list[dict]) -> None:
        pass
