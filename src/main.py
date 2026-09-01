from os import environ

from aiohttp.web import Application, Request, Response, json_response, run_app
from microsoft_agents.hosting.aiohttp import (
    jwt_authorization_middleware,
    start_agent_process,
)

import bot  # noqa: F401 - registers the activity handler on import
from config import ADAPTER, AGENT_APP, CONNECTION_MANAGER


async def health(_request: Request) -> Response:
    return json_response({"status": "hello world"})


async def messages(request: Request) -> Response:
    return await start_agent_process(request, AGENT_APP, ADAPTER)


# jwt_authorization_middleware enforces that incoming requests carry a valid
# Bot Framework JWT before reaching the handler - without it, /api/messages
# would process any unauthenticated request (confirmed while testing). It
# reads app["agent_configuration"] to know which app/tenant to validate
# against - omitting it fails with "Agent Authentication configuration not
# found" (also confirmed while testing). Scoped to a sub-app on /api so it
# doesn't also block the plain health check on / (confirmed that mistake too -
# a single Application's middlewares apply to every route, not just some).
API_APP = Application(middlewares=[jwt_authorization_middleware])
API_APP["agent_configuration"] = CONNECTION_MANAGER.get_default_connection_configuration()
API_APP.router.add_post("/messages", messages)

APP = Application()
APP.router.add_get("/", health)
APP.add_subapp("/api", API_APP)

if __name__ == "__main__":
    run_app(APP, host="0.0.0.0", port=int(environ.get("PORT", 8000)))
