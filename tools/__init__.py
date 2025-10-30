"""Tool function definitions for news, fact, and scam verification.

All tool functions follow ADK best practices:
- Single str parameter named 'request'
- Return dict with status and data fields
- No complex type annotations (ToolContext removed)
"""

from google.adk.tools import FunctionTool

from .news_tools import (
    fetch_news_evidence,
    research_news_with_perplexity,
)
from .fact_tools import (
    check_factcheck_api,
    research_fact_with_perplexity,
)
from .scam_tools import (
    scan_urls_with_virustotal,
    research_scam_with_perplexity,
    analyze_scam_sentiment,
)


# News verification tools
NEWS_API_TOOL = FunctionTool(fetch_news_evidence)
NEWS_PERPLEXITY_TOOL = FunctionTool(research_news_with_perplexity)

# Fact-checking tools
FACT_CHECK_TOOL = FunctionTool(check_factcheck_api)
FACT_PERPLEXITY_TOOL = FunctionTool(research_fact_with_perplexity)

# Scam detection tools
VIRUSTOTAL_TOOL = FunctionTool(scan_urls_with_virustotal)
SCAM_PERPLEXITY_TOOL = FunctionTool(research_scam_with_perplexity)
SCAM_SENTIMENT_TOOL = FunctionTool(analyze_scam_sentiment)


__all__ = [
    # News tools
    "NEWS_API_TOOL",
    "NEWS_PERPLEXITY_TOOL",
    "fetch_news_evidence",
    "research_news_with_perplexity",
    
    # Fact tools
    "FACT_CHECK_TOOL",
    "FACT_PERPLEXITY_TOOL",
    "check_factcheck_api",
    "research_fact_with_perplexity",
    
    # Scam tools
    "VIRUSTOTAL_TOOL",
    "SCAM_PERPLEXITY_TOOL",
    "SCAM_SENTIMENT_TOOL",
    "scan_urls_with_virustotal",
    "research_scam_with_perplexity",
    "analyze_scam_sentiment",
]
