from typing import Optional

from sqlmodel import Field, PrimaryKeyConstraint, SQLModel


class OpenWeatherHourly(SQLModel, table=True):
    """One Call API: hourly forecast. One row per hour."""

    __table_args__ = (PrimaryKeyConstraint("latitude", "longitude", "hourly_dt"),)

    latitude: float = Field(alias="root.lat")
    longitude: float = Field(alias="root.lon")
    hourly_dt: int = Field(alias="root.hourly[*].dt")
    temp: Optional[float] = Field(default=None, alias="root.hourly[*].temp")
    feels_like: Optional[float] = Field(default=None, alias="root.hourly[*].feels_like")
    pressure: Optional[int] = Field(default=None, alias="root.hourly[*].pressure")
    humidity: Optional[int] = Field(default=None, alias="root.hourly[*].humidity")
    dew_point: Optional[float] = Field(default=None, alias="root.hourly[*].dew_point")
    uvi: Optional[float] = Field(default=None, alias="root.hourly[*].uvi")
    clouds: Optional[int] = Field(default=None, alias="root.hourly[*].clouds")
    visibility: Optional[int] = Field(default=None, alias="root.hourly[*].visibility")
    wind_speed: Optional[float] = Field(default=None, alias="root.hourly[*].wind_speed")
    wind_deg: Optional[int] = Field(default=None, alias="root.hourly[*].wind_deg")
    wind_gust: Optional[float] = Field(default=None, alias="root.hourly[*].wind_gust")
    pop: Optional[float] = Field(default=None, alias="root.hourly[*].pop")

    weather_id: Optional[int] = Field(
        default=None, alias="root.hourly[*].weather[0].id"
    )
    weather_main: Optional[str] = Field(
        default=None, alias="root.hourly[*].weather[0].main"
    )
    weather_description: Optional[str] = Field(
        default=None, alias="root.hourly[*].weather[0].description"
    )
