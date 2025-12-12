from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlmodel import Field, SQLModel


class PolygonTickers(SQLModel, table=True):
    active: bool = Field(alias="root.active")
    cik: Optional[str] = Field(alias="root.cik", default=None)
    composite_figi: Optional[str] = Field(alias="root.composite_figi", default=None)
    currency_name: str = Field(max_length=3, alias="root.currency_name")
    last_updated_utc: DateTime = Field(alias="root.last_updated_utc")
    locale: str = Field(alias="root.locale")
    market: str = Field(alias="root.market")
    name: str = Field(alias="root.name")
    primary_exchange: Optional[str] = Field(alias="root.primary_exchange", default=None)
    share_class_figi: Optional[str] = Field(alias="root.share_class_figi", default=None)
    ticker: str = Field(primary_key=True, alias="root.ticker")
    type: str = Field(alias="root.type")
