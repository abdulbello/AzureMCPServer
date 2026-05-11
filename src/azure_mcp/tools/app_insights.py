"""Tool: query_app_insights — runs a KQL query against an Application Insights /
Log Analytics workspace."""

from datetime import timedelta

from azure.monitor.query import LogsQueryClient, LogsQueryStatus

from ..auth import get_credential
from ..config import Config


def query_app_insights(
    kql_query: str,
    workspace_id: str | None = None,
    timespan_hours: int = Config.DEFAULT_KQL_TIMESPAN_HOURS,
) -> dict:
    """Run a KQL query against an Application Insights (Log Analytics) workspace.

    The LLM is expected to write the KQL. Common tables:
      - requests (timestamp, name, url, resultCode, duration, success, operation_Name)
      - exceptions (timestamp, type, outerMessage, operation_Name, severityLevel)
      - traces (timestamp, message, severityLevel, operation_Name)
      - dependencies (timestamp, name, target, success, duration, resultCode)
      - customEvents (timestamp, name, customDimensions)

    Always include a `| take N` and a `| where timestamp > ago(Xh)` in your query.

    Args:
        kql_query: A valid KQL query string.
        workspace_id: Log Analytics workspace ID. Falls back to the value
            in AZURE_LOG_ANALYTICS_WORKSPACE_ID if not provided.
        timespan_hours: How far back to query. Capped at MAX_KQL_TIMESPAN_HOURS.

    Returns:
        Dict with `columns`, `rows` (capped at MAX_KQL_ROWS), and `row_count`.
    """
    workspace = workspace_id or Config.LOG_ANALYTICS_WORKSPACE_ID
    if not workspace:
        return {
            "error": (
                "No Log Analytics workspace ID provided. Either pass workspace_id "
                "or set AZURE_LOG_ANALYTICS_WORKSPACE_ID in the environment."
            )
        }

    # Cap the timespan to prevent runaway queries.
    hours = max(1, min(timespan_hours, Config.MAX_KQL_TIMESPAN_HOURS))

    client = LogsQueryClient(get_credential())
    response = client.query_workspace(
        workspace_id=workspace,
        query=kql_query,
        timespan=timedelta(hours=hours),
    )

    if response.status == LogsQueryStatus.FAILURE:
        return {"error": str(response.partial_error or "Query failed")}

    table = response.tables[0] if response.tables else None
    if table is None:
        return {"columns": [], "rows": [], "row_count": 0}

    columns = [c for c in table.columns]
    rows = [list(r) for r in table.rows][: Config.MAX_KQL_ROWS]

    # Convert non-serializable types (datetime, etc.) to strings.
    rows = [[str(v) if v is not None else None for v in row] for row in rows]

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "truncated": len(table.rows) > Config.MAX_KQL_ROWS,
        "timespan_hours": hours,
    }
