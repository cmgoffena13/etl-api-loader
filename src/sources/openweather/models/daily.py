from typing import Optional

from sqlmodel import Field, PrimaryKeyConstraint, SQLModel


class OpenWeatherDaily(SQLModel, table=True):
    """One Call API: daily forecast. One row per day."""

    __table_args__ = (PrimaryKeyConstraint("latitude", "longitude", "daily_dt"),)

    latitude: float = Field(alias="root.lat")
    longitude: float = Field(alias="root.lon")
    daily_dt: int = Field(alias="root.daily[*].dt")
    sunrise: Optional[int] = Field(default=None, alias="root.daily[*].sunrise")
    sunset: Optional[int] = Field(default=None, alias="root.daily[*].sunset")
    moonrise: Optional[int] = Field(default=None, alias="root.daily[*].moonrise")
    moonset: Optional[int] = Field(default=None, alias="root.daily[*].moonset")
    moon_phase: Optional[float] = Field(default=None, alias="root.daily[*].moon_phase")
    summary: Optional[str] = Field(default=None, alias="root.daily[*].summary")
    pressure: Optional[int] = Field(default=None, alias="root.daily[*].pressure")
    humidity: Optional[int] = Field(default=None, alias="root.daily[*].humidity")
    dew_point: Optional[float] = Field(default=None, alias="root.daily[*].dew_point")
    wind_speed: Optional[float] = Field(default=None, alias="root.daily[*].wind_speed")
    wind_deg: Optional[int] = Field(default=None, alias="root.daily[*].wind_deg")
    wind_gust: Optional[float] = Field(default=None, alias="root.daily[*].wind_gust")
    clouds: Optional[int] = Field(default=None, alias="root.daily[*].clouds")
    pop: Optional[float] = Field(default=None, alias="root.daily[*].pop")
    uvi: Optional[float] = Field(default=None, alias="root.daily[*].uvi")
    rain: Optional[float] = Field(default=None, alias="root.daily[*].rain")
    snow: Optional[float] = Field(default=None, alias="root.daily[*].snow")

    temp_day: Optional[float] = Field(default=None, alias="root.daily[*].temp.day")
    temp_min: Optional[float] = Field(default=None, alias="root.daily[*].temp.min")
    temp_max: Optional[float] = Field(default=None, alias="root.daily[*].temp.max")
    temp_night: Optional[float] = Field(default=None, alias="root.daily[*].temp.night")
    temp_eve: Optional[float] = Field(default=None, alias="root.daily[*].temp.eve")
    temp_morn: Optional[float] = Field(default=None, alias="root.daily[*].temp.morn")

    feels_like_day: Optional[float] = Field(
        default=None, alias="root.daily[*].feels_like.day"
    )
    feels_like_night: Optional[float] = Field(
        default=None, alias="root.daily[*].feels_like.night"
    )
    feels_like_eve: Optional[float] = Field(
        default=None, alias="root.daily[*].feels_like.eve"
    )
    feels_like_morn: Optional[float] = Field(
        default=None, alias="root.daily[*].feels_like.morn"
    )

    weather_id: Optional[int] = Field(default=None, alias="root.daily[*].weather[0].id")
    weather_main: Optional[str] = Field(
        default=None, alias="root.daily[*].weather[0].main"
    )
    weather_description: Optional[str] = Field(
        default=None, alias="root.daily[*].weather[0].description"
    )
