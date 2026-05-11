# Demo prompts

Use these in Claude Desktop after configuring the MCP server. Pick a flow,
record a ~60 second Loom for the README.

## Flow 1 — "Is my app healthy?"

1. *"What App Services do I have in the `prod-rg` resource group?"*
   → `list_resources` with `resource_type=Microsoft.Web/sites`
2. *"Is `payments-api` running and healthy?"*
   → `get_app_service_status`
3. *"Show me the last hour of exceptions for it from App Insights."*
   → `query_app_insights` with KQL Claude writes itself
4. *"Anything stuck in the dead-letter queue on my Service Bus?"*
   → `list_service_bus_queues`

## Flow 2 — "Investigate a spike in errors"

1. *"Query App Insights for the count of failed requests grouped by URL in the
   last 2 hours."*
2. *"For the worst offender, show me the top 5 exception messages."*
3. *"What's the average response time for that endpoint right now?"*

## Flow 3 — "Tour my subscription"

1. *"What resource groups do I have?"*
2. *"What's in the `shared-rg`?"*
3. *"Pick the most interesting App Service and check its health."*
