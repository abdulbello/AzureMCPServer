"""MCP server entry point. Registers tools and runs over stdio."""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import Config
from .tools.app_insights import query_app_insights
from .tools.app_service import get_app_service_status
from .tools.resource_groups import list_resource_groups
from .tools.resources import list_resources
from .tools.service_bus import list_service_bus_queues

# Log to stderr — stdout is reserved for the MCP protocol over stdio.
logging.basicConfig(level=logging.INFO, format="[azure-mcp] %(message)s")
logger = logging.getLogger(__name__)

server = Server("azure-mcp")


# ---------------------------------------------------------------------------
# Tool definitions. Descriptions are written FOR THE LLM — be explicit about
# what each tool does, when to use it, and what arguments mean.
# ---------------------------------------------------------------------------
TOOLS: list[Tool] = [
    Tool(
        name="list_resource_groups",
        description=(
            "List Azure resource groups in the configured subscription. "
            "Use this to orient yourself before drilling into specific resources."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name_filter": {
                    "type": "string",
                    "description": "Optional case-insensitive substring filter on RG name.",
                },
            },
        },
    ),
    Tool(
        name="list_resources",
        description=(
            "List resources within a resource group, optionally filtered by type. "
            "Common types: 'Microsoft.Web/sites' (App Services), "
            "'Microsoft.DocumentDB/databaseAccounts' (Cosmos DB), "
            "'Microsoft.ServiceBus/namespaces' (Service Bus), "
            "'Microsoft.Insights/components' (Application Insights)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "resource_group": {"type": "string"},
                "resource_type": {
                    "type": "string",
                    "description": "Optional Azure resource type filter.",
                },
            },
            "required": ["resource_group"],
        },
    ),
    Tool(
        name="get_app_service_status",
        description=(
            "Get the running state, hostname, HTTPS-only flag, SKU, and a derived "
            "'healthy' boolean for a specific App Service. Use this to answer "
            "'is X running?' or 'is X healthy?' questions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "resource_group": {"type": "string"},
                "name": {"type": "string", "description": "App Service name."},
            },
            "required": ["resource_group", "name"],
        },
    ),
    Tool(
        name="query_app_insights",
        description=(
            "Run a KQL query against an Application Insights (Log Analytics) workspace. "
            "YOU write the KQL. Common tables: "
            "`requests` (timestamp, name, url, resultCode, duration, success, operation_Name), "
            "`exceptions` (timestamp, type, outerMessage, operation_Name, severityLevel), "
            "`traces` (timestamp, message, severityLevel), "
            "`dependencies` (timestamp, name, target, success, duration), "
            "`customEvents`. "
            "ALWAYS include `| where timestamp > ago(Xh)` and `| take 50`. "
            "Results are capped at 100 rows. Default timespan is 1 hour, max 24."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "kql_query": {"type": "string", "description": "A KQL query."},
                "workspace_id": {
                    "type": "string",
                    "description": "Log Analytics workspace ID. Optional if AZURE_LOG_ANALYTICS_WORKSPACE_ID is set.",
                },
                "timespan_hours": {
                    "type": "integer",
                    "description": "How far back to query (1-24). Default 1.",
                },
            },
            "required": ["kql_query"],
        },
    ),
    Tool(
        name="list_service_bus_queues",
        description=(
            "List queues in a Service Bus namespace with active, dead-letter, "
            "and scheduled message counts. Use this to investigate stuck messages "
            "or check queue depth."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "resource_group": {"type": "string"},
                "namespace_name": {"type": "string"},
            },
            "required": ["resource_group", "namespace_name"],
        },
    ),
]


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch a tool call. Each tool is sync; we run in a thread to avoid
    blocking the event loop."""
    logger.info(f"call_tool: {name} args={arguments}")

    def run() -> Any:
        if name == "list_resource_groups":
            return list_resource_groups(name_filter=arguments.get("name_filter"))
        if name == "list_resources":
            return list_resources(
                resource_group=arguments["resource_group"],
                resource_type=arguments.get("resource_type"),
            )
        if name == "get_app_service_status":
            return get_app_service_status(
                resource_group=arguments["resource_group"],
                name=arguments["name"],
            )
        if name == "query_app_insights":
            return query_app_insights(
                kql_query=arguments["kql_query"],
                workspace_id=arguments.get("workspace_id"),
                timespan_hours=arguments.get("timespan_hours", 1),
            )
        if name == "list_service_bus_queues":
            return list_service_bus_queues(
                resource_group=arguments["resource_group"],
                namespace_name=arguments["namespace_name"],
            )
        raise ValueError(f"Unknown tool: {name}")

    try:
        result = await asyncio.to_thread(run)
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    except Exception as e:
        logger.exception("Tool call failed")
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": type(e).__name__, "message": str(e)}),
            )
        ]


async def _run() -> None:
    Config.validate()
    logger.info(
        f"Starting azure-mcp server (subscription={Config.SUBSCRIPTION_ID[:8]}...)"
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
