from src.settings import config
from src.sources.base import (
    APIConfig,
    APIEndpointConfig,
    NextUrlPaginationConfig,
)
from src.sources.polygon.models.tickers import PolygonTickers

POLYGON_CONFIG = APIConfig(
    name="polygon",
    base_url="https://api.massive.com/v3/reference",
    type="rest",
    authentication_strategy="bearer",
    authentication_params={"token": config.POLYGON_API_KEY},
    pagination_strategy="next_url",
    pagination=NextUrlPaginationConfig(
        next_url_key="next_url",
    ),
    endpoints={
        "tickers": APIEndpointConfig(
            json_entrypoint="results",
            backoff_starting_delay=60,
            tables=[
                PolygonTickers,
            ],
        )
    },
)
