import gradio as gr
import asyncio
import os
from magentic_ui.task_team import get_task_team
from magentic_ui.magentic_ui_config import MagenticUIConfig
from magentic_ui.types import RunPaths

# It's recommended to load secrets from the environment for security
JINA_API_TOKEN = os.environ.get("JINA_API_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

async def analyze_flat(url):
    """
    This function takes a URL, runs the flat analysis workflow, and returns the results.
    """
    if not all([JINA_API_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, OPENAI_API_KEY]):
        return "Error: Missing one or more required API tokens in the environment."

    # Configure Magentic UI
    config = MagenticUIConfig(
        jina_api_token=JINA_API_TOKEN,
        telegram_bot_token=TELEGRAM_BOT_TOKEN,
        telegram_chat_id=TELEGRAM_CHAT_ID,
        model_client_configs={
            "orchestrator": {
                "provider": "OpenAIChatCompletionClient",
                "config": {"model": "gpt-4-turbo", "api_key": OPENAI_API_KEY},
            }
        },
    )

    # Define paths for the run
    paths = RunPaths(
        internal_root_dir=".",
        external_root_dir=".",
        run_suffix="",
        internal_run_dir=".",
        external_run_dir=".",
    )

    # Get the team of agents
    team = await get_task_team(magentic_ui_config=config, paths=paths)

    # Run the workflow
    if hasattr(team, "workflow"):
        try:
            formatted_output = await team.workflow(url)
            return formatted_output
        except Exception as e:
            return f"An error occurred: {e}"
    else:
        return "Error: The 'workflow' attribute is not available on the team object."

# Define the Gradio interface
iface = gr.Interface(
    fn=lambda url: asyncio.run(analyze_flat(url)),
    inputs=gr.Textbox(lines=1, placeholder="Enter the URL of the flat listing here..."),
    outputs=gr.Markdown(),
    title="ImmoSpider Flat Analyzer",
    description="Enter a URL of a flat listing to get an AI-powered analysis and a Telegram notification.",
)

if __name__ == "__main__":
    iface.launch()
