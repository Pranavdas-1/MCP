from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio, ast
from pathlib import Path

async def main():
    server_path = Path(__file__).parent / "first_mcp_server.py"
    server_params = StdioServerParameters(command="python", args=[str(server_path)])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            # print(tools)
            result = await session.call_tool(
                "get_forecast",
                arguments={"latitude": 40.7, "longitude": -74.0}
            )
           
            data = ast.literal_eval(result.content[0].text)

            print(data[0]["name"], "-", data[0]["temperature"])

asyncio.run(main())
