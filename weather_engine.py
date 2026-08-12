from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json


EGYPT_LOCATIONS = {
    "Cairo": (30.0444, 31.2357),
    "Giza": (29.9870, 31.2118),
    "Alexandria": (31.2001, 29.9187),
    "Ismailia": (30.5965, 32.2715),
    "Port Said": (31.2653, 32.3019),
    "Suez": (29.9668, 32.5498),
    "Mansoura": (31.0409, 31.3785),
    "Luxor": (25.6872, 32.6396),
    "Aswan": (24.0889, 32.8998),
    "Hurghada": (27.2579, 33.8116),
}


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}


def _fallback(location: str) -> dict:
    """Safe offline fallback so the demo still runs without internet."""
    hour = datetime.now().hour
    lat, _ = EGYPT_LOCATIONS[location]
    base = 29 if lat > 29 else 34
    daily = max(0, 6 - abs(hour - 13) * 0.45)
    return {
        "location": location,
        "latitude": lat,
        "longitude": EGYPT_LOCATIONS[location][1],
        "current_temperature": round(base + daily * 0.5, 1),
        "current_humidity": round(48 + max(0, 4 - abs(hour - 5)) * 3, 0),
        "wind_speed": 14.0,
        "precipitation_probability": 5.0,
        "weather_code": 0,
        "description": "Offline simulated clear conditions",
        "forecast_max_temp": round(base + 4.0, 1),
        "forecast_min_temp": round(base - 5.0, 1),
        "sunrise": "06:00",
        "sunset": "18:45",
        "source": "Offline fallback",
        "forecast": [],
    }


def get_weather(location: str) -> dict:
    if location not in EGYPT_LOCATIONS:
        location = "Cairo"
    lat, lon = EGYPT_LOCATIONS[location]
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code,is_day",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,shortwave_radiation,wind_speed_10m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max,shortwave_radiation_sum",
        "forecast_days": 2,
        "timezone": "auto",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)
    try:
        req = Request(url, headers={"User-Agent": "AI-Resource-Optimizer/1.0"})
        with urlopen(req, timeout=6) as response:
            payload = json.loads(response.read().decode("utf-8"))

        current = payload["current"]
        daily = payload["daily"]
        hourly = payload["hourly"]
        forecast = []
        for i in range(min(12, len(hourly["time"]))):
            forecast.append({
                "time": hourly["time"][i],
                "temperature": hourly["temperature_2m"][i],
                "humidity": hourly["relative_humidity_2m"][i],
                "rain_probability": hourly["precipitation_probability"][i],
                "solar_radiation": hourly["shortwave_radiation"][i],
                "wind": hourly["wind_speed_10m"][i],
            })

        return {
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "current_temperature": current["temperature_2m"],
            "current_humidity": current["relative_humidity_2m"],
            "wind_speed": current["wind_speed_10m"],
            "precipitation_probability": daily["precipitation_probability_max"][0],
            "weather_code": current["weather_code"],
            "description": WEATHER_CODES.get(current["weather_code"], "Variable conditions"),
            "forecast_max_temp": daily["temperature_2m_max"][0],
            "forecast_min_temp": daily["temperature_2m_min"][0],
            "sunrise": daily["sunrise"][0][-5:],
            "sunset": daily["sunset"][0][-5:],
            "source": "Open-Meteo forecast",
            "forecast": forecast,
        }
    except Exception:
        return _fallback(location)
