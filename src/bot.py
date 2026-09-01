from microsoft_agents.hosting.core import TurnContext, TurnState

from agent import run_agent
from config import AGENT_APP

# In-memory conversation history keyed by Teams conversation id. Lost on
# container restart - fine for this POC. Swap for persistent storage if that
# becomes a problem.
_history: dict[str, list] = {}


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    conversation_id = context.activity.conversation.id
    reply, updated_history = await run_agent(
        context.activity.text, _history.get(conversation_id, [])
    )
    _history[conversation_id] = updated_history
    await context.send_activity(reply)
