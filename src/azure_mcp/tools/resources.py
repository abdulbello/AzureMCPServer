"""Tool: list_resources."""

from azure.mgmt.resource import ResourceManagementClient

from ..auth import get_credential
from ..config import Config


def list_resources(
    resource_group: str,
    resource_type: str | None = None,
) -> list[dict]:
    """List resources within a resource group.

    Args:
        resource_group: The resource group name.
        resource_type: Optional Azure resource type, e.g. 'Microsoft.Web/sites',
            'Microsoft.DocumentDB/databaseAccounts', 'Microsoft.ServiceBus/namespaces',
            'Microsoft.Insights/components'.

    Returns:
        A list of {name, type, location, id} dicts.
    """
    client = ResourceManagementClient(get_credential(), Config.SUBSCRIPTION_ID)

    filter_expr = f"resourceType eq '{resource_type}'" if resource_type else None
    results = []
    for r in client.resources.list_by_resource_group(resource_group, filter=filter_expr):
        results.append(
            {
                "name": r.name,
                "type": r.type,
                "location": r.location,
                "id": r.id,
            }
        )
    return results
