from typing import Optional

from sqlmodel import Field, PrimaryKeyConstraint, SQLModel


class OpenWeatherCurrent(SQLModel, table=True):
    """One Call API: root location + current snapshot. One row per response."""

    __table_args__ = (PrimaryKeyConstraint("latitude", "longitude", "current_dt"),)

    latitude: float = Field(alias="root.lat")
    longitude: float = Field(alias="root.lon")
    timezone: Optional[str] = Field(default=None, alias="root.timezone")
    timezone_offset: Optional[int] = Field(default=None, alias="root.timezone_offset")

    current_dt: Optional[int] = Field(default=None, alias="root.current.dt")
    current_sunrise: Optional[int] = Field(default=None, alias="root.current.sunrise")
    current_sunset: Optional[int] = Field(default=None, alias="root.current.sunset")
    current_temp: Optional[float] = Field(default=None, alias="root.current.temp")
    current_feels_like: Optional[float] = Field(
        default=None, alias="root.current.feels_like"
    )
    current_pressure: Optional[int] = Field(default=None, alias="root.current.pressure")
    current_humidity: Optional[int] = Field(default=None, alias="root.current.humidity")
    current_dew_point: Optional[float] = Field(
        default=None, alias="root.current.dew_point"
    )
    current_uvi: Optional[float] = Field(default=None, alias="root.current.uvi")
    current_clouds: Optional[int] = Field(default=None, alias="root.current.clouds")
    current_visibility: Optional[int] = Field(
        default=None, alias="root.current.visibility"
    )
    current_wind_speed: Optional[float] = Field(
        default=None, alias="root.current.wind_speed"
    )
    current_wind_deg: Optional[int] = Field(default=None, alias="root.current.wind_deg")

    current_weather_id: Optional[int] = Field(
        default=None, alias="root.current.weather[0].id"
    )
    current_weather_main: Optional[str] = Field(
        default=None, alias="root.current.weather[0].main"
    )
    current_weather_description: Optional[str] = Field(
        default=None, alias="root.current.weather[0].description"
    )
    current_weather_icon: Optional[str] = Field(
        default=None, alias="root.current.weather[0].icon"
    )
