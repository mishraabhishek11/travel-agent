from datetime import datetime, timedelta
import httpx
from services.cache import get_cache, set_cache

async def fetch_currency_rates(base_currency: str) -> dict[str, float]:
    """Fetch currency exchange rates from an external API."""
    cache_key = f"currency_{base_currency}"
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://v6.exchangerate-api.com/v6/6c382afb11c24e1d41e898a1/latest/{base_currency}"
        )
        response.raise_for_status()
        data = response.json()
        
        rates = data.get("conversion_rates", {})
        set_cache(cache_key, rates, ttl=3600)  # Cache for 1 hour
        return rates