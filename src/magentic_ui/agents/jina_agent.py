from autogen_agentchat.agents import Agent
from autogen_core.models import ChatCompletionClient
from magentic_ui.tools import get_url_content
import json

class JinaAgent(Agent):
    def __init__(self, name: str, api_token: str, model_client: ChatCompletionClient):
        super().__init__(name)
        self.api_token = api_token
        self.model_client = model_client

    async def _parse_content_with_llm(self, content: str) -> dict:
        """
        Uses an LLM to parse the markdown content from the Jina API to extract flat details.
        """
        prompt = f"""
        Here is the content of a webpage about a flat rental:
        ---
        {content}
        ---

        Please extract the following details from the text and provide them in a JSON format:
        - title: The title of the listing.
        - address: The full address of the flat.
        - price: The rental price.
        - size: The size of the flat (e.g., in square meters).
        - description: A summary of the flat's key features.

        If any detail is not available, please use "N/A".
        Your response should be only the JSON object, without any other text before or after it.
        """

        response = await self.model_client.create(
            messages=[{"role": "user", "content": prompt}]
        )

        details = {}
        try:
            response_content = response.choices[0].message.content
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()

            details = json.loads(response_content)
            details["raw_content"] = content
        except (json.JSONDecodeError, IndexError) as e:
            details = {
                "error": "Could not parse LLM response for flat details.",
                "raw_content": content,
            }

        return details

    async def a_get_content(self, url: str) -> dict:
        """
        Fetches content from a URL using the Jina API and parses it with an LLM.
        """
        raw_content = await get_url_content(url, self.api_token)
        if raw_content.startswith("Error:"):
            return {"error": raw_content}

        return await self._parse_content_with_llm(raw_content)
