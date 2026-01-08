from autogen_agentchat.agents import Agent
from autogen_core.models import ChatCompletionClient

class LLMAnalyserAgent(Agent):
    def __init__(self, name: str, model_client: ChatCompletionClient):
        super().__init__(name)
        self.model_client = model_client

    def _clean_description(self, description: str) -> str:
        """
        Cleanses the flat description by removing HTML tags and other formatting.
        """
        # This is a simple example, a more robust implementation would be needed for production
        import re
        clean_text = re.sub('<[^<]+?>', '', description)
        return clean_text

    async def a_analyze_description(self, flat_details: dict) -> dict:
        """
        Analyzes the flat description using an LLM to generate an analysis, rating, and personal message.
        """
        description = flat_details.get("description", "")
        clean_description = self._clean_description(description)

        prompt = f"""
        Here is the description of a flat:
        {clean_description}

        Please provide an analysis of the flat, a rating from 1 to 5, and a personal message.
        Return the result in a JSON format with the keys "analysis", "rating", and "personal_message".
        """

        response = await self.model_client.create(
            messages=[{"role": "user", "content": prompt}]
        )

        # This is a simple example, a more robust implementation would be needed for production
        import json
        try:
            response_content = response.choices[0].message.content
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0].strip()
            analysis = json.loads(response_content)
        except (json.JSONDecodeError, IndexError):
            analysis = {
                "analysis": "Error: Could not parse LLM response.",
                "rating": 0,
                "personal_message": "",
            }

        return analysis
