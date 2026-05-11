"""Tool: get_app_service_status."""

from azure.mgmt.web import WebSiteManagementClient

from ..auth import get_credential
from ..config import Config


def get_app_service_status(resource_group: str, name: str) -> dict:
    """Get the current status and key configuration of an App Service.

    Args:
        resource_group: The resource group containing the App Service.
        name: The App Service name.

    Returns:
        Dict with state, hostname, runtime, HTTPS-only flag, SKU, and a
        derived `healthy` boolean for quick interpretation.
    """
    client = WebSiteManagementClient(get_credential(), Config.SUBSCRIPTION_ID)
    site = client.web_apps.get(resource_group, name)

    state = site.state or "Unknown"
    https_only = bool(site.https_only)
    healthy = state == "Running" and https_only

    return {
        "name": site.name,
        "state": state,
        "default_hostname": site.default_host_name,
        "kind": site.kind,
        "https_only": https_only,
        "enabled": site.enabled,
        "last_modified_utc": site.last_modified_time_utc.isoformat()
        if site.last_modified_time_utc
        else None,
        "location": site.location,
        "sku": site.sku.name if getattr(site, "sku", None) else None,
        "healthy": healthy,
    }
