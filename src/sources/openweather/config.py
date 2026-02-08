from src.settings import config
from src.sources.base import APIConfig, APIEndpointConfig, TableConfig
from src.sources.openweather.models.current import OpenWeatherCurrent
from src.sources.openweather.models.daily import OpenWeatherDaily
from src.sources.openweather.models.hourly import OpenWeatherHourly
from src.sources.openweather.models.minute import OpenWeatherMinute

OPENWEATHER_CONFIG = APIConfig(
    name="openweather",
    base_url="https://api.openweathermap.org/data/3.0",
    type="rest",
    default_params={
        "lat": 37.774929,
        "lon": -122.419416,
        "units": "imperial",
        "appid": config.OPENWEATHER_API_KEY,
    },
    endpoints={
        "onecall": APIEndpointConfig(
            tables=[
                TableConfig(data_model=OpenWeatherCurrent),
                TableConfig(data_model=OpenWeatherMinute),
                TableConfig(data_model=OpenWeatherHourly),
                TableConfig(data_model=OpenWeatherDaily),
            ]
        )
    },
)
