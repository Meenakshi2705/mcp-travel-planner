from mcp.server.fastmcp import FastMCP
import random
from datetime import datetime

mcp = FastMCP("season-server", host="0.0.0.0", port=8000)

season_map = {
    "summer": ["Ooty", "Manali", "Shimla"],
    "winter": ["Goa", "Kerala"],
    "monsoon": ["Coorg", "Munnar"]
}

def get_season(month):
    if month in [3, 4, 5, 6]:
        return "summer"
    elif month in [11, 12, 1, 2]:
        return "winter"
    else:
        return "monsoon"

@mcp.tool()
async def get_season_city():
    month = datetime.now().month
    season = get_season(month)
    city = random.choice(season_map[season])
    return {
        "city": city,
        "season": season,
        "reason": f"{city} is best during {season}"
    }

if __name__ == "__main__":
    mcp.run(transport="sse")