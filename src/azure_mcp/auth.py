"""Azure authentication. Uses DefaultAzureCredential — picks up `az login`,
environment variables, managed identity, etc., in that order."""

from azure.identity import DefaultAzureCredential

_credential: DefaultAzureCredential | None = None


def get_credential() -> DefaultAzureCredential:
    """Return a cached DefaultAzureCredential instance."""
    global _credential
    if _credential is None:
        _credential = DefaultAzureCredential()
    return _credential
