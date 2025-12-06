from src.pipeline.read.authentication.auth import AuthAuthenticationStrategy
from src.pipeline.read.authentication.base import BaseAuthenticationStrategy
from src.pipeline.read.authentication.bearer import BearerAuthenticationStrategy
from src.sources.base import APIConfig


class AuthenticationStrategyFactory:
    _strategies = {
        "auth": AuthAuthenticationStrategy,
        "bearer": BearerAuthenticationStrategy,
    }

    @classmethod
    def get_supported_strategies(cls) -> list[type[BaseAuthenticationStrategy]]:
        return list(cls._strategies.keys())

    @classmethod
    def create_strategy(cls, source: APIConfig, **kwargs) -> BaseAuthenticationStrategy:
        try:
            strategy = cls._strategies[source.authentication_strategy]
            return strategy(**kwargs)
        except KeyError:
            raise ValueError(
                f"Unsupported authentication strategy: {source.authentication_strategy}. Supported strategies: {cls.get_supported_strategies()}"
            )
