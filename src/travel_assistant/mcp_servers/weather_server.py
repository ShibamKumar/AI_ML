import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")


async def _geocode_city(city: str) -> tuple[float, float]:
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )
        response.raise_for_status()
        payload = response.json()

    results = payload.get("results") or []
    if not results:
        raise ValueError(f"Could not find city: {city}")

    return float(results[0]["latitude"]), float(results[0]["longitude"])


@mcp.tool()
async def get_weather_forecast(city: str, days: int = 3) -> dict:
    """Return daily weather forecast for the given city using Open-Meteo."""
    days = max(1, min(days, 7))
    latitude, longitude = await _geocode_city(city)

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
                "timezone": "auto",
                "forecast_days": days,
            },
        )
        response.raise_for_status()
        data = response.json()

    daily = data.get("daily", {})
    timeline = []
    for i in range(len(daily.get("time", []))):
        timeline.append(
            {
                "date": daily["time"][i],
                "temp_min_c": daily["temperature_2m_min"][i],
                "temp_max_c": daily["temperature_2m_max"][i],
                "precipitation_probability_max": daily["precipitation_probability_max"][i],
                "weather_code": daily["weather_code"][i],
            }
        )

    return {"city": city, "forecast": timeline, "provider": "Open-Meteo"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
