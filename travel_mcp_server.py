from mcp.server.fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("travel-server", host="0.0.0.0", port=8001)

def get_weather_api_key():
    """Read from environment — Streamlit Cloud injects st.secrets as env vars for subprocesses."""
    return os.getenv("OPENWEATHER_API_KEY")

async def fetch_weather(city: str) -> dict:
    api_key = get_weather_api_key()

    if not api_key:
        return {"error": "OPENWEATHER_API_KEY not set.", "city": city,
                "description": "Unknown", "temp_c": "N/A",
                "feels_like": "N/A", "humidity": "N/A"}

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )
    async with httpx.AsyncClient() as http:
        res = await http.get(url)
        if res.status_code != 200:
            return {"error": "Weather data unavailable.", "city": city,
                    "description": "Unavailable", "temp_c": "N/A",
                    "feels_like": "N/A", "humidity": "N/A"}

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
    """Returns raw weather data for the given city. No LLM — data only."""
    return await fetch_weather(city)

if __name__ == "__main__":
    mcp.run(transport="sse")
