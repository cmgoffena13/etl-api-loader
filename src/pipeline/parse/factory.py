from src.pipeline.parse.base import BaseParser
from src.pipeline.parse.json import JSONParser
from src.sources.base import APIConfig, APIEndpointConfig


class ParserFactory:
    _parsers = {
        "json": JSONParser,
    }

    @classmethod
    def get_supported_parsers(cls) -> list[type[BaseParser]]:
        return list(cls._parsers.keys())

    @classmethod
    def create_parser(
        cls, source: APIConfig, endpoint_config: APIEndpointConfig
    ) -> BaseParser:
        try:
            parser_class = cls._parsers[source.parse_type]
            return parser_class(endpoint_config=endpoint_config)
        except KeyError:
            raise ValueError(
                f"Unsupported parser type: {source.parse_type}. Supported types: {cls.get_supported_parsers()}"
            )
