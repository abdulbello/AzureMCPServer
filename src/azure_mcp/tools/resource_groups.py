"""Tool: list_resource_groups."""

from azure.mgmt.resource import ResourceManagementClient

from ..auth import get_credential
from ..config import Config


def list_resource_groups(name_filter: str | None = None) -> list[dict]:
    """List resource groups in the configured subscription.

    Args:
        name_filter: Optional case-insensitive substring filter on RG name.

    Returns:
        A list of {name, location, tags} dicts.
    """
    client = ResourceManagementClient(get_credential(), Config.SUBSCRIPTION_ID)

    results = []
    for rg in client.resource_groups.list():
        if name_filter and name_filter.lower() not in rg.name.lower():
            continue
        results.append(
            {
                "name": rg.name,
                "location": rg.location,
                "tags": rg.tags or {},
            }
        )
    return results
