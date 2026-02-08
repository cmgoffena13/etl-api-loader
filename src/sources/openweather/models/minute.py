from typing import Optional

from sqlmodel import Field, PrimaryKeyConstraint, SQLModel


class OpenWeatherMinute(SQLModel, table=True):
    """One Call API: minutely forecast. One row per minute, keyed by location + dt."""

    __table_args__ = (PrimaryKeyConstraint("latitude", "longitude", "minute_dt"),)

    latitude: float = Field(alias="root.lat")
    longitude: float = Field(alias="root.lon")
    minute_dt: int = Field(alias="root.minutely[*].dt")
    precipitation: Optional[float] = Field(
        default=None, alias="root.minutely[*].precipitation"
    )
