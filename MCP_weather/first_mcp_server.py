from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("weather")

@mcp.tool()
async def get_forecast(latitude: float, longitude:float) -> str:
    """Get weather forcast for a location."""
    async with httpx.AsyncClient() as client:
        points = await client.get(f"https://api.weather.gov/points/{latitude},{longitude}")
        forecast_url = points.json()["properties"]["forecast"]
        forecast = await client.get(forecast_url)
        return str(forecast.json()["properties"]["periods"][:3])

if __name__ == "__main__":
    mcp.run(transport="stdio")