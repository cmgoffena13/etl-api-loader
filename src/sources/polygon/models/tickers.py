from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlmodel import Field, PrimaryKeyConstraint, SQLModel


class PolygonTickers(SQLModel, table=True):
    active: bool = Field(alias="root.active")
    cik: Optional[str] = Field(alias="root.cik", default=None)
    composite_figi: Optional[str] = Field(alias="root.composite_figi", default=None)
    currency_name: Optional[str] = Field(alias="root.currency_name", default=None)
    last_updated_utc: Optional[DateTime] = Field(
        alias="root.last_updated_utc", default=None
    )
    locale: str = Field(alias="root.locale")
    market: str = Field(alias="root.market")
    name: Optional[str] = Field(alias="root.name", default=None)
    primary_exchange: Optional[str] = Field(alias="root.primary_exchange", default=None)
    share_class_figi: Optional[str] = Field(alias="root.share_class_figi", default=None)
    ticker: str = Field(alias="root.ticker")
    type: Optional[str] = Field(alias="root.type", default=None)

    __table_args__ = (PrimaryKeyConstraint("ticker", "market"),)
