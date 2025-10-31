"""Shared configuration for the news & information verification system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# Default model for all agents
# Note: gemini-2.5-flash currently has compatibility issues with ADK telemetry
# Reverting to gemini-2.0-flash until ADK is updated
MODEL: Final[str] = "gemini-2.0-flash"


@dataclass(frozen=True)
class StateKeys:
    """Centralized session state keys for consistent data flow."""

    # News lane outputs
    NEWS_API: str = "news_api_data"
    NEWS_FACT: str = "news_fact_data"
    NEWS_PERPLEXITY: str = "news_perplexity_data"
    NEWS_SUMMARY: str = "news_summary"

    # Fact lane outputs
    FACT_PRIMARY: str = "fact_primary_data"
    FACT_PERPLEXITY: str = "fact_perplexity_data"
    FACT_SUMMARY: str = "fact_summary"

    # Scam lane outputs
    SCAM_SENTIMENT: str = "scam_sentiment_data"
    SCAM_PERPLEXITY: str = "scam_perplexity_data"
    SCAM_LINK: str = "scam_link_data"
    SCAM_SUMMARY: str = "scam_summary"

    # Final output
    FINAL_REPORT: str = "final_report"


# Global instance
STATE_KEYS: Final[StateKeys] = StateKeys()
