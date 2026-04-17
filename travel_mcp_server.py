from mcp.server.fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("travel-server", host="0.0.0.0", port=8001)

# ✅ Only fetches weather data - no LLM
async def fetch_weather(city: str) -> dict:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )
    async with httpx.AsyncClient() as http:
        res = await http.get(url)
        if res.status_code != 200:
            return {"error": "Weather data unavailable."}
        
        data = res.json()
        return {
            "city"       : city,
            "description": data["weather"][0]["description"].capitalize(),
            "temp_c"     : data["main"]["temp"],
            "feels_like" : data["main"]["feels_like"],
            "humidity"   : data["main"]["humidity"],
        }

@mcp.tool()
async def plan_trip(city: str):
    """
    Returns raw weather data for the given city.
    """
    weather_data = await fetch_weather(city)
    # ✅ Just return raw data — NO LLM here
    return weather_data

if __name__ == "__main__":
    mcp.run(transport="sse")
