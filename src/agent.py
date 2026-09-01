from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

from services.foundry import build_model

# No tools yet - first increment is a conversational agent with memory only.
# Tools (reading a codebase, writing code, opening GitLab MRs) come later,
# one at a time.
teams_agent = Agent(
    build_model(),
    system_prompt=(
        "You are a helpful assistant chatting with a user in Microsoft Teams. "
        "Keep replies concise and conversational."
    ),
)


async def run_agent(
    message: str, history: list[ModelMessage]
) -> tuple[str, list[ModelMessage]]:
    result = await teams_agent.run(message, message_history=history)
    return result.output, result.all_messages()
