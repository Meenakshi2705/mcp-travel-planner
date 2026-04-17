import json
from mcp import ClientSession
from mcp.client.sse import sse_client


class MCPClientHTTP:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def call_tool(self, tool_name: str, payload: dict):
        async with sse_client(f"{self.base_url}/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, payload)

                # result.content is a list of TextContent objects
                text = result.content[0].text

                # Try to parse JSON (season server returns a dict)
                try:
                    return json.loads(text)
                except (json.JSONDecodeError, TypeError):
                    return text