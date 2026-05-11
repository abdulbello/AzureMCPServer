"""Tool: list_service_bus_queues."""

from azure.mgmt.servicebus import ServiceBusManagementClient

from ..auth import get_credential
from ..config import Config


def list_service_bus_queues(resource_group: str, namespace_name: str) -> list[dict]:
    """List Service Bus queues in a namespace, including message counts.

    Args:
        resource_group: The resource group containing the Service Bus namespace.
        namespace_name: The Service Bus namespace name.

    Returns:
        A list of dicts with queue name, status, and message counts (active,
        dead-lettered, scheduled, transfer dead-lettered).
    """
    client = ServiceBusManagementClient(get_credential(), Config.SUBSCRIPTION_ID)

    results = []
    for q in client.queues.list_by_namespace(resource_group, namespace_name):
        counts = q.count_details
        results.append(
            {
                "name": q.name,
                "status": q.status,
                "active_message_count": counts.active_message_count if counts else None,
                "dead_letter_message_count": counts.dead_letter_message_count
                if counts
                else None,
                "scheduled_message_count": counts.scheduled_message_count
                if counts
                else None,
                "transfer_dead_letter_message_count": counts.transfer_dead_letter_message_count
                if counts
                else None,
                "max_size_mb": q.max_size_in_megabytes,
            }
        )
    return results
