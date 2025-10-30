"""News verification tool functions."""


def fetch_news_evidence(request: str) -> dict:
    """
    Fetch licensed news articles related to a claim using GNews API.
    
    Args:
        request: The news claim or topic to search for
        
    Returns:
        dict with:
            - status: 'success' or 'error'
            - articles: List of {title, url, source, published_date} dicts
            - error: Error message if status='error'
    """
    from ..services.gnews_client import search_news
    
    try:
        articles = search_news(request)
        return {
            "status": "success",
            "articles": articles,
            "query": request,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": request,
        }


def research_news_with_perplexity(request: str) -> dict:
    """
    Research news claims using Perplexity AI's web search capabilities.
    
    Args:
        request: The news claim to research
        
    Returns:
        dict with:
            - status: 'success' or 'error'
            - answer: Perplexity's researched answer
            - citations: List of source URLs
            - error: Error message if status='error'
    """
    from ..services.perplexity_client import query_perplexity
    
    prompt = f"""Research this news claim and verify its accuracy:
    
Claim: {request}

Provide:
1. Whether the claim is supported by credible news sources
2. Key facts and evidence
3. Any contradictory information
4. Cite all sources"""
    
    try:
        result = query_perplexity(prompt)
        return {
            "status": "success",
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
            "query": request,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": request,
        }


__all__ = ["fetch_news_evidence", "research_news_with_perplexity"]
