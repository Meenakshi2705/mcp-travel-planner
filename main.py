import os
from dotenv import load_dotenv
from groq import Groq
from mcp_client import MCPClientHTTP

load_dotenv()

class AIService:
    def __init__(self):
        self.server1 = MCPClientHTTP("http://localhost:8000")
        self.server2 = MCPClientHTTP("http://localhost:8001")
        self.client  = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def _generate(self, prompt: str) -> str:
        """✅ LLM lives here in the CLIENT - correct place"""
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    async def process_query(self, user_input: str):
        try:
            # Step 1: Get season & city from MCP Server 1
            print("🔧 Calling Server 1 (season)...")
            res1 = await self.server1.call_tool("get_season_city", {})
            print("📍 Server1 Output:", res1)

            city   = res1["city"]
            season = res1["season"]
            reason = res1["reason"]

            # Step 2: Get weather DATA from MCP Server 2 (raw data only)
            print("🔧 Calling Server 2 (weather data)...")
            weather_data = await self.server2.call_tool("plan_trip", {"city": city})
            print("🌤️ Server2 Output:", weather_data)

            # Step 3: ✅ CLIENT builds prompt and calls LLM
            prompt = f"""
            User asked: {user_input}

            Suggested city : {city}
            Season         : {season}
            Reason         : {reason}

            Current Weather in {city}:
            - Condition  : {weather_data.get('description', 'N/A')}
            - Temperature: {weather_data.get('temp_c', 'N/A')}°C 
                           (feels like {weather_data.get('feels_like', 'N/A')}°C)
            - Humidity   : {weather_data.get('humidity', 'N/A')}%

            Using the above data, create a friendly 3-day travel itinerary 
            for {city}. Mention weather conditions and keep it 
            beginner-friendly.
            """
            return self._generate(prompt)  # ✅ LLM called here in CLIENT

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"❌ Error: {str(e)}"
