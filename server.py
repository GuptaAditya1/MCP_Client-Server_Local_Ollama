from fastmcp import FastMCP
import httpx
import certifi
from urllib.parse import quote

# Create the MCP instance
mcp = FastMCP("Wikipedia MCP Server")

@mcp.tool
async def wikipedia_summary(topic: str) -> str:
    """
    Fetch a short summary of a Wikipedia article.
    First searches for the best matching article, then retrieves its summary.
    """
    headers = {"User-Agent": "FastMCP-WikipediaBot/1.0 (https://example.com/contact)"}
    
    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        # Step 1: Search for the topic to find the best matching article
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(topic)}&format=json&srlimit=1"
        
        search_resp = await client.get(search_url, headers=headers)
        if search_resp.status_code != 200:
            return f"Wikipedia search API error: {search_resp.status_code}"
        
        search_data = search_resp.json()
        search_results = search_data.get("query", {}).get("search", [])
        
        if not search_results:
            return f"No Wikipedia articles found for '{topic}'."
        
        # Get the title of the best match
        best_match_title = search_results[0]["title"]
        
        # Step 2: Fetch the summary of the matched article
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(best_match_title)}"
        
        summary_resp = await client.get(summary_url, headers=headers)
        if summary_resp.status_code == 200:
            data = summary_resp.json()
            title = data.get("title", "")
            extract = data.get("extract", "")
            return f"**{title}**\n\n{extract}"
        elif summary_resp.status_code == 404:
            return f"Article '{best_match_title}' was found but summary could not be retrieved."
        else:
            return f"Wikipedia summary API error: {summary_resp.status_code}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
