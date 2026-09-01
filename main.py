from os import environ

from aiohttp.web import Application, Request, Response, json_response, run_app
from dotenv import load_dotenv
from microsoft_agents.activity import load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.aiohttp import CloudAdapter, start_agent_process
from microsoft_agents.hosting.core import (
    AgentApplication,
    Authorization,
    MemoryStorage,
    TurnContext,
    TurnState,
)

load_dotenv()
agents_sdk_config = load_configuration_from_env(environ)

STORAGE = MemoryStorage()
CONNECTION_MANAGER = MsalConnectionManager(**agents_sdk_config)
ADAPTER = CloudAdapter(connection_manager=CONNECTION_MANAGER)
AUTHORIZATION = Authorization(STORAGE, CONNECTION_MANAGER, **agents_sdk_config)

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE, adapter=ADAPTER, authorization=AUTHORIZATION, **agents_sdk_config
)


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    await context.send_activity(f"echo: {context.activity.text}")


async def health(_request: Request) -> Response:
    return json_response({"status": "hello world"})


async def messages(request: Request) -> Response:
    return await start_agent_process(request, AGENT_APP, ADAPTER)


APP = Application()
APP.router.add_get("/", health)
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    run_app(APP, host="0.0.0.0", port=int(environ.get("PORT", 8000)))
