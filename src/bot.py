from microsoft_agents.hosting.core import TurnContext, TurnState

from config import AGENT_APP


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    await context.send_activity(f"echo: {context.activity.text}")
