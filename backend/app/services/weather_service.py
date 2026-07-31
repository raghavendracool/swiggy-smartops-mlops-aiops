import requests


def weather_code_to_text(code):
    weather_map = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail",
    }

    return weather_map.get(code, "Unknown weather")


def weather_severity_for_model(raining_num, precipitation_mm, weather_code):
    if raining_num == 1:
        if precipitation_mm >= 5:
            return "Heavy Rain"

        if precipitation_mm >= 2:
            return "Moderate Rain"

        return "Light Rain"

    if weather_code == 3:
        return "Cloudy"

    if weather_code in [1, 2]:
        return "Partly Cloudy"

    return "Clear"


def fetch_weather(latitude, longitude, fallback_raining_num=0):
    try:
        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
            "timezone": "auto",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})

        temperature = float(current.get("temperature_2m", 0.0))
        precipitation = float(current.get("precipitation", 0.0))
        weather_code = int(current.get("weather_code", 0))
        wind_speed = float(current.get("wind_speed_10m", 0.0))

        rainy_codes = list(range(51, 68)) + [80, 81, 82, 95, 96, 99]

        raining_num = 1 if precipitation > 0 or weather_code in rainy_codes else 0

        return {
            "temperature": temperature,
            "precipitation_mm": precipitation,
            "weather_code": weather_code,
            "weather_text": weather_code_to_text(weather_code),
            "weather_condition": "Rain / Drizzle" if raining_num == 1 else "Clear / Normal",
            "weather_severity": weather_severity_for_model(
                raining_num,
                precipitation,
                weather_code
            ),
            "wind_speed": wind_speed,
            "raining_num": raining_num,
            "weather_api_status": "success",
        }

    except Exception as e:
        raining_num = int(fallback_raining_num)

        return {
            "temperature": 0.0,
            "precipitation_mm": 0.0,
            "weather_code": 0,
            "weather_text": f"Weather API failed: {str(e)}",
            "weather_condition": "Rain / Drizzle" if raining_num == 1 else "Clear / Normal",
            "weather_severity": "Light Rain" if raining_num == 1 else "Clear",
            "wind_speed": 0.0,
            "raining_num": raining_num,
            "weather_api_status": "failed",
        }