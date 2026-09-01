# teams-agent-app

The agent that runs behind [Christian's Teams bot](https://github.com/ChristianKatka/teams-agent) - receives messages via the Bot Framework, answers them using a pydantic-ai agent backed by Azure AI Foundry.

Deployed automatically: the VM in the `teams-agent` repo clones this repo and runs it via `docker compose` on every deploy - see `bootstrap.sh`.

## Layout

```
src/
├── main.py     # HTTP server (aiohttp), routes, JWT auth middleware
├── bot.py      # Bot Framework activity handlers
├── config.py   # SDK/auth wiring (Microsoft 365 Agents SDK, UserManagedIdentity)
├── services/   # external clients (Azure AI Foundry, etc.)
└── tools/      # agent tools
```
