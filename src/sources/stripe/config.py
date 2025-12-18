from src.settings import config
from src.sources.base import (
    APIConfig,
    APIEndpointConfig,
    CursorPaginationConfig,
    TableConfig,
)
from src.sources.stripe.models.charges import StripeCharges

STRIPE_CONFIG = APIConfig(
    name="stripe",
    base_url="https://api.stripe.com/v1",
    type="rest",
    json_entrypoint="data",
    authentication_strategy="bearer",
    authentication_params={"token": config.STRIPE_API_KEY},
    pagination_strategy="cursor",
    pagination=CursorPaginationConfig(
        cursor_param="starting_after",
        next_cursor_key="data[-1].id",
        limit_param="limit",
        limit=100,
    ),
    endpoints={
        "charges": APIEndpointConfig(
            json_entrypoint="data",
            tables=[
                TableConfig(data_model=StripeCharges),
            ],
        )
    },
)
