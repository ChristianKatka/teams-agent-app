from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

from services.foundry import build_model
from tools.coding_agent import implement_feature

teams_agent = Agent(
    build_model(),
    system_prompt=(
        "You are a helpful assistant chatting with a user in Microsoft Teams. "
        "Keep replies concise and conversational. If the user asks you to build, "
        "add, or change a feature in the frontend project, use the "
        "implement_feature tool - it opens a merge request for a human to "
        "review, it never merges on its own. Tell the user this may take a "
        "few minutes."
    ),
)
teams_agent.tool_plain(implement_feature)


async def run_agent(
    message: str, history: list[ModelMessage]
) -> tuple[str, list[ModelMessage]]:
    result = await teams_agent.run(message, message_history=history)
    return result.output, result.all_messages()
