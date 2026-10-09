import asyncio

from fastapi import APIRouter, HTTPException
from services.currency import fetch_currency_rates
from services.places import fetch_places
from model import TravelRequestModel
from services.weather import fetch_weather

router = APIRouter(
    prefix="/plan",
    tags=["Travel Plan"],
)

@router.post("/")
async def create_travel_plan(
    travel_request: TravelRequestModel,
):
    """Aggregate Weather, Currency, and Places data into a single travel plan."""

    if travel_request.start_date > travel_request.end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date",
        )
    
    trip_days = (travel_request.end_date - travel_request.start_date).days

    if trip_days < 1:
        raise HTTPException(
            status_code=400,
            detail="Travel plan must be at least 1 day long",
        )
    
    if trip_days > 14:
        raise HTTPException(
            status_code=400,
            detail="Travel plan cannot be longer than 14 days",
        )

    # Here, you would typically call the services to aggregate the travel data (Weather, Currency, Places) based on the travel_request parameters.

    # Weather Data, Currency Rates, and Places data would be fetched and aggregated into a single response.
    
    weather_data, places_data, currency_rates = await asyncio.gather(
        fetch_weather(
            destination=travel_request.destination,
            start_date=travel_request.start_date,
            end_date=travel_request.end_date,
        ),
        fetch_places(travel_request.destination),
        fetch_currency_rates(travel_request.base_currency)
    )
    
    return {
        "message": "Travel plan created successfully",
        "weather_data": weather_data,
        "places_data": places_data,
        "currency_rates": currency_rates,
    }