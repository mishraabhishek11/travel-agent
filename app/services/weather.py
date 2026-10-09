import httpx
from datetime import date
from model import WeatherResponseModel
from services.cache import get_cache, set_cache

async def fetch_weather(
        destination: str,
        start_date: date,
        end_date: date
)->list[WeatherResponseModel]:
    
    cache_key = f"{destination}_{start_date}_{end_date}"
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weatherapi.com/v1/forecast.json",
            params={
                "key": "930971becfa941f882053344220412",
                "q": destination,
                "dt": start_date,
                "end_dt": end_date
            }
        )
        response.raise_for_status()
        data = response.json()
        
        forcasts = []

        for day in data['forecast']['forecastday']:
            forecast = WeatherResponseModel(
                date=day['date'],
                condition=day['day']['condition']['text'],
                temperature_high=day['day']['maxtemp_c'],
                temperature_low=day['day']['mintemp_c'],
                humidity=day['day']['avghumidity'],
                rain_chance=day['day']['daily_chance_of_rain']
            )
            forcasts.append(forecast)

        set_cache(cache_key, forcasts, ttl=3600)  # Cache for 1 hour
        return forcasts