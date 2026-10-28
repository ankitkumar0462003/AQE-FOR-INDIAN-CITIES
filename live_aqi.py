"""One beginner-friendly API function for current, modeled US AQI."""
import requests

API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# Latitude and longitude for major cities.
CITIES = {
    "Delhi": (28.6139, 77.2090),
    "Ludhiana": (30.9010, 75.8573),
    "Amritsar": (31.6340, 74.8723),
    "Chandigarh": (30.7333, 76.7794),
    "Mumbai": (19.0760, 72.8777),
    "Jaipur": (26.9124, 75.7873),
    "Kolkata": (22.5726, 88.3639)
}


def aqi_category(aqi):
    if aqi is None:
        return "Not available"
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for sensitive groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very unhealthy"
    return "Hazardous"


def get_live_aqi(city):
    """Ask Open-Meteo for model estimates and return a small dictionary."""
    latitude, longitude = CITIES[city]
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "us_aqi,pm2_5,pm10,nitrogen_dioxide,carbon_monoxide,ozone",
        "timezone": "Asia/Kolkata"
    }
    response = requests.get(API_URL, params=params, timeout=8)
    response.raise_for_status()
    result = response.json()
    if result.get("error"):
        raise ValueError(result.get("reason", "API error"))
    current = result.get("current", {})
    if not current.get("time"):
        raise ValueError("No current air quality data returned")
    return {"values": current, "units": result.get("current_units", {})}
