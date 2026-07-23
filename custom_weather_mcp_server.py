from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

mcp = FastMCP("Weather MCP Server")

@mcp.tool()
def get_current_weather(city: str):
    # url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            }
        )
    
    data = response.json()
    
    if response.status_code != 200:
        return data
    
    return {
        "city": data["name"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }

@mcp.tool()
def get_forecast(city:str):
    response = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"
            }
        )
    
    data = response.json()
    
    forcast = []

    for day in data["list"]:
        forcast.append({
            "date": day["dt_txt"],
            "temperature_c": day["main"]["temp"],
            "feels_like_c": day["main"]["feels_like"],
            "humidity": day["main"]["humidity"],
            "condition": day["weather"][0]["description"],
            "wind_speed": day["wind"]["speed"]
        })
    
    return {
            "city": city,
            "forcast": forcast
        }

if __name__ == "__main__":
    mcp.run()