import aiohttp
import json

async def get_url_content(url: str, api_token: str) -> str:
    """
    Fetches the content of a URL using the Jina AI reader API.

    Args:
        url: The URL to fetch the content from.
        api_token: The Jina AI reader API token.

    Returns:
        The content of the URL as a string.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    data = {"url": url}

    async with aiohttp.ClientSession() as session:
        async with session.post("https://r.jina.ai/", headers=headers, json=data) as response:
            if response.status == 200:
                return await response.text()
            else:
                return f"Error: Received status code {response.status}"
