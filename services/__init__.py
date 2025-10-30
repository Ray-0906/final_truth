"""Service layer initialization - HTTP clients for external APIs."""

from .gnews_client import search_news
from .factcheck_client import search_fact_checks
from .virustotal_client import scan_url
from .perplexity_client import query_perplexity

__all__ = [
    "search_news",
    "search_fact_checks",
    "scan_url",
    "query_perplexity",
]
