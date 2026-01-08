from autogen_agentchat.agents import Agent
import telegram

class TelegramAgent(Agent):
    def __init__(self, name: str, bot_token: str, chat_id: str):
        super().__init__(name)
        self.bot = telegram.Bot(token=bot_token)
        self.chat_id = chat_id

    def _format_message(self, flat_details: dict, analysis: dict) -> str:
        """
        Formats the flat details, analysis, rating, and personal message into a single string.
        """
        title = flat_details.get('title', 'N/A')
        address = flat_details.get('address', 'N/A')
        price = flat_details.get('price', 'N/A')
        size = flat_details.get('size', 'N/A')

        llm_analysis = analysis.get('analysis', 'N/A')
        rating = analysis.get('rating', 'N/A')
        personal_message = analysis.get('personal_message', 'N/A')

        return (
            f"*New Flat Listing Found!*\n\n"
            f"*Title:* {title}\n"
            f"*Address:* {address}\n"
            f"*Price:* {price}\n"
            f"*Size:* {size}\n\n"
            f"*AI Analysis:*\n{llm_analysis}\n\n"
            f"*Rating:* {rating}/5\n"
            f"*Personal Message:*\n{personal_message}"
        )

    async def a_send_message(self, flat_details: dict, analysis: dict):
        """
        Formats and sends a message to the specified Telegram chat.
        """
        message = self._format_message(flat_details, analysis)
        await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')
