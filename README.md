# Travel Agent

A FastAPI service that aggregates **weather**, **places of interest** and **currency rates** into a single travel plan for a destination. It is a learning project for async API design, concurrent I/O, response caching and Server-Sent Events (SSE) streaming.

## Features

- **Travel plan:** One request returns a weather forecast, curated places and currency rates for the trip.
- **Concurrent fetching:** Weather, places and currency are fetched together with `asyncio.gather`.
- **Streaming:** An SSE endpoint emits progress events as each data source completes.
- **Caching:** Weather and currency responses are cached in memory for 1 hour.
- **Validation:** Requests are validated with Pydantic. Invalid trip dates return 400.

## Tech Stack

- Python, FastAPI, Uvicorn
- Pydantic for models and validation
- httpx for async HTTP calls
- [WeatherAPI](https://www.weatherapi.com/) for forecasts
- [ExchangeRate-API](https://www.exchangerate-api.com/) for currency rates

## Project Structure

```
app/
├── model.py            # TravelRequestModel, WeatherResponseModel, PlaceModel
├── routes/
│   ├── planner.py      # POST /plan/         - aggregated travel plan
│   └── stream.py       # POST /stream/plan   - SSE streaming plan
└── services/
    ├── weather.py      # WeatherAPI forecast (cached 1h)
    ├── currency.py     # Exchange rates (cached 1h)
    ├── places.py       # Built-in places database (manali, goa, jaipur)
    └── cache.py        # Simple in-memory TTL cache
```

## Getting Started

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

Run the server from the `app/` directory (the modules use top-level imports such as `from services.weather import ...`), pointing Uvicorn at the FastAPI app that includes the `planner` and `stream` routers:

```bash
cd app
uvicorn main:app --reload
```

Interactive docs are then available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.

## API

### Request body (both endpoints)

```json
{
  "destination": "goa",
  "start_date": "2026-12-01",
  "end_date": "2026-12-05",
  "base_currency": "INR"
}
```

`base_currency` is optional and defaults to `INR`.

### `POST /plan/`

Returns the aggregated plan:

```json
{
  "message": "Travel plan created successfully",
  "weather_data": [],
  "places_data": [],
  "currency_rates": {}
}
```

### `POST /stream/plan`

Streams `text/event-stream` events in this order: `start`, `weather`, `weather_complete`, `options`, `options_complete`, `currency`, `currency_complete`, `complete`.

### Validation rules

| Condition                     | Response |
| ----------------------------- | -------- |
| `start_date` after `end_date` | 400      |
| Trip shorter than 1 day       | 400      |
| Trip longer than 14 days      | 400      |
| Malformed body                | 422      |

## Supported Destinations

Places are served from a built-in dataset: **Manali**, **Goa** and **Jaipur** (case-insensitive). Other destinations return an empty places list; weather and currency still work.

## Configuration

> **Security note:** the WeatherAPI and ExchangeRate-API keys are currently hardcoded in `services/weather.py` and `services/currency.py`. Move them to environment variables (loaded from `.env` via `python-dotenv`), rotate the exposed keys, and make sure `.env` stays in `.gitignore`.

## Planned Work

- Move API keys to environment configuration
- Add the FastAPI app entry point (`main.py`) and CORS settings
- Tests for routes and services
- Consistent error shape (`{ "error": { "code", "message" } }`)
- Replace the static places dataset with a real places API
- Docker support
