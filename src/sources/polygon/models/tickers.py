from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime


class PolygonTicker(BaseModel):
    active: bool
    cik: str
    composite_figi: str
    currency_name: str
    last_updated_utc: DateTime
    locale: str
    market: str
    name: str
    primary_exchange: str
    share_class_figi: str
    ticker: str
    type: str
