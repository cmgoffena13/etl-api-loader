from typing import Optional

from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime


class PolygonTicker(BaseModel):
    active: bool
    cik: Optional[str] = None
    composite_figi: Optional[str] = None
    currency_name: str
    last_updated_utc: DateTime
    locale: str
    market: str
    name: str
    primary_exchange: Optional[str] = None
    share_class_figi: Optional[str] = None
    ticker: str
    type: str
