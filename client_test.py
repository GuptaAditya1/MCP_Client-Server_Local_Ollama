import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def main():
    async with client:
        result = await client.call_tool("wikipedia_summary", {"topic": "Python (programming language)"})
        print(result.data)

asyncio.run(main())
