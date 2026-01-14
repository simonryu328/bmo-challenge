"""Mock weather tool that returns simulated weather data."""

import random
from langchain_core.tools import tool


# Mock weather data for various cities
WEATHER_DATA = {
    "new york": {"temp_f": 45, "condition": "Partly Cloudy", "humidity": 65},
    "los angeles": {"temp_f": 72, "condition": "Sunny", "humidity": 40},
    "chicago": {"temp_f": 38, "condition": "Windy", "humidity": 55},
    "houston": {"temp_f": 68, "condition": "Clear", "humidity": 70},
    "phoenix": {"temp_f": 85, "condition": "Sunny", "humidity": 15},
    "san francisco": {"temp_f": 58, "condition": "Foggy", "humidity": 80},
    "seattle": {"temp_f": 48, "condition": "Rainy", "humidity": 85},
    "miami": {"temp_f": 78, "condition": "Humid", "humidity": 90},
    "denver": {"temp_f": 42, "condition": "Snow", "humidity": 45},
    "boston": {"temp_f": 40, "condition": "Cloudy", "humidity": 60},
    "london": {"temp_f": 50, "condition": "Rainy", "humidity": 75},
    "paris": {"temp_f": 55, "condition": "Overcast", "humidity": 70},
    "tokyo": {"temp_f": 60, "condition": "Clear", "humidity": 50},
    "sydney": {"temp_f": 75, "condition": "Sunny", "humidity": 55},
}


@tool
def WeatherMockTool(city: str) -> str:
    """Get mock weather information for a city.

    Args:
        city: The name of the city to get weather for

    Returns:
        A formatted weather report string
    """
    city_lower = city.lower().strip()

    if city_lower in WEATHER_DATA:
        data = WEATHER_DATA[city_lower]
    else:
        # Generate random weather for unknown cities
        data = {
            "temp_f": random.randint(30, 90),
            "condition": random.choice(
                ["Sunny", "Cloudy", "Rainy", "Windy", "Clear", "Partly Cloudy"]
            ),
            "humidity": random.randint(20, 90),
        }

    temp_c = round((data["temp_f"] - 32) * 5 / 9, 1)

    return (
        f"Weather in {city.title()}:\n"
        f"  Temperature: {data['temp_f']}°F ({temp_c}°C)\n"
        f"  Condition: {data['condition']}\n"
        f"  Humidity: {data['humidity']}%"
    )
