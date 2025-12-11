from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlmodel import Field, SQLModel


class PolygonTickers(SQLModel, table=True):
    active: bool
    cik: Optional[str] = None
    composite_figi: Optional[str] = None
    currency_name: str = Field(max_length=3)
    last_updated_utc: DateTime
    locale: str
    market: str
    name: str
    primary_exchange: Optional[str] = None
    share_class_figi: Optional[str] = None
    ticker: str = Field(primary_key=True)
    type: str
