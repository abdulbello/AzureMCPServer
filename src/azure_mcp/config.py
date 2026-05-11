"""Configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Server configuration. Loaded once at startup."""

    SUBSCRIPTION_ID: str = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
    LOG_ANALYTICS_WORKSPACE_ID: str = os.environ.get(
        "AZURE_LOG_ANALYTICS_WORKSPACE_ID", ""
    )

    # Safety guardrails — values intentionally conservative.
    MAX_KQL_ROWS: int = 100
    MAX_KQL_TIMESPAN_HOURS: int = 24
    DEFAULT_KQL_TIMESPAN_HOURS: int = 1

    @classmethod
    def validate(cls) -> None:
        """Fail fast at startup if required config is missing."""
        if not cls.SUBSCRIPTION_ID:
            raise RuntimeError(
                "AZURE_SUBSCRIPTION_ID is not set. "
                "Copy .env.example to .env and fill it in, "
                "or export the variable in your shell."
            )
