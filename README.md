# Azure Resources MCP Server

A Model Context Protocol (MCP) server that lets AI assistants like Claude
inspect your Azure environment in natural language.

> *"Is my payments-api healthy?"*
> → Claude calls `get_app_service_status` and `query_app_insights`, reports
> the state, and surfaces the last hour of exceptions.

Read-only by design. No write operations, no scary side effects.

---

## Why I built this

I wanted to combine the Azure stack I work with every day (App Services,
Application Insights, Service Bus) with the Model Context Protocol — to see
how far a small, well-scoped server can go in making cloud operations feel
conversational.

## What it does

Five tools, exposed over MCP:

| Tool | Purpose |
|---|---|
| `list_resource_groups` | Orientation: what's in this subscription? |
| `list_resources` | Drill into a resource group, optionally filtered by type. |
| `get_app_service_status` | Running state, hostname, HTTPS, SKU, derived health. |
| `query_app_insights` | Run KQL against Log Analytics. Claude writes the query. |
| `list_service_bus_queues` | Queue names with active and dead-letter counts. |

## Demo

*(Drop a Loom or GIF here when ready.)*

See [`demo/demo.md`](demo/demo.md) for suggested prompts.

## Quick start

### 1. Prerequisites

- Python 3.10+
- An Azure subscription you can read from
- `az` CLI installed and `az login` completed

### 2. Install

```bash
git clone <this repo>
cd azure-mcp-server
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env and set AZURE_SUBSCRIPTION_ID
# (and AZURE_LOG_ANALYTICS_WORKSPACE_ID if you'll use KQL)
```

To find your Log Analytics workspace ID, open your Application Insights
resource in the Azure portal → **Logs** → look at the top-right info bar.

### 4. Wire it into Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows). Add:

```json
{
  "mcpServers": {
    "azure": {
      "command": "/ABSOLUTE/PATH/TO/azure-mcp-server/.venv/bin/python",
      "args": ["-m", "azure_mcp.server"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "your-subscription-id",
        "AZURE_LOG_ANALYTICS_WORKSPACE_ID": "your-workspace-id"
      }
    }
  }
}
```

Restart Claude Desktop. The Azure tools should appear under the 🔌 menu.

## Safety

Designed to be safe to demo:

- **Read-only.** No write SDK clients are imported, so the server cannot
  create, modify, restart, or delete resources.
- **Result caps.** KQL queries return at most 100 rows.
- **Timespan caps.** KQL queries default to 1 hour and max out at 24 hours.
- **No secret logging.** Credentials and connection strings are never echoed.

## Architecture

```
src/azure_mcp/
├── server.py             # MCP entry point, tool registration & dispatch
├── auth.py               # DefaultAzureCredential singleton
├── config.py             # Env-loaded config + guardrails
└── tools/
    ├── resource_groups.py
    ├── resources.py
    ├── app_service.py
    ├── app_insights.py
    └── service_bus.py
```

Each tool is a plain Python function. `server.py` registers them with the
MCP SDK and dispatches calls.

Auth uses `DefaultAzureCredential`, which transparently picks up `az login`,
environment variables, managed identity, or VS Code login — whichever is
available.

## What's next (out of scope for v1)

- Write operations behind a confirmation flow
- Azure SQL query tool (read-only `SELECT` with table allowlist)
- Cost / billing queries
- Cross-subscription support
- Function App invocation history

## License

MIT
