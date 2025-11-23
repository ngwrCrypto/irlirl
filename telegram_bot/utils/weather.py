import httpx
from config import LATITUDE, LONGITUDE

async def get_weather() -> str:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "timezone": "auto"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            current = data.get("current", {})
            temp = current.get("temperature_2m", "N/A")
            wind = current.get("wind_speed_10m", "N/A")
            code = current.get("weather_code", 0)

            # WMO Weather interpretation codes (simplified)
            # https://open-meteo.com/en/docs
            if code == 0:
                emoji = "☀️" # Clear sky
                desc = "Sunny"
            elif code in [1, 2, 3]:
                emoji = "☁️" # Cloudy
                desc = "Cloudy"
            elif code in [45, 48]:
                emoji = "🌫️" # Fog
                desc = "Foggy"
            elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                emoji = "🌧️" # Rain
                desc = "Rain"
            elif code in [71, 73, 75, 77, 85, 86]:
                emoji = "❄️" # Snow
                desc = "Snow"
            elif code in [95, 96, 99]:
                emoji = "⛈️" # Thunderstorm
                desc = "Storm"
            else:
                emoji = "🌡"
                desc = "Normal"

            return f"Погода сьогодні: {desc} {emoji}, 🌡 {temp}°C, 💨 {wind} км/год"

    except Exception as e:
        return f"Не вдалося отримати погоду: {e}"

async def get_weather_forecast() -> str:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 2
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            # Index 1 is tomorrow (0 is today)
            code = daily.get("weather_code", [0, 0])[1]
            temp_max = daily.get("temperature_2m_max", [0, 0])[1]
            temp_min = daily.get("temperature_2m_min", [0, 0])[1]

            # WMO Weather interpretation codes (simplified)
            if code == 0:
                emoji = "☀️"
                desc = "Sunny"
            elif code in [1, 2, 3]:
                emoji = "☁️"
                desc = "Cloudy"
            elif code in [45, 48]:
                emoji = "🌫️"
                desc = "Foggy"
            elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                emoji = "🌧️"
                desc = "Rain"
            elif code in [71, 73, 75, 77, 85, 86]:
                emoji = "❄️"
                desc = "Snow"
            elif code in [95, 96, 99]:
                emoji = "⛈️"
                desc = "Storm"
            else:
                emoji = "🌡"
                desc = "Normal"

            return f"Прогноз на завтра: {desc} {emoji}, 🌡 {temp_min}°C ... {temp_max}°C"

    except Exception as e:
        return f"Не вдалося отримати прогноз: {e}"
