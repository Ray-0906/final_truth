"""Fact checking tool functions."""


def check_factcheck_api(request: str) -> dict:
    """
    Look up fact-checks from Google Fact Check Tools API.
    
    Args:
        request: The claim to fact-check
        
    Returns:
        dict with:
            - status: 'success' or 'error'
            - claims: List of {claim, claimant, rating, url, source} dicts
            - error: Error message if status='error'
    """
    from ..services.factcheck_client import search_fact_checks
    
    try:
        claims = search_fact_checks(request)
        return {
            "status": "success",
            "claims": claims,
            "query": request,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": request,
        }


def research_fact_with_perplexity(request: str) -> dict:
    """
    Research factual claims using Perplexity AI's deep research.
    
    Args:
        request: The factual claim to verify
        
    Returns:
        dict with:
            - status: 'success' or 'error'
            - answer: Perplexity's researched answer
            - citations: List of source URLs
            - error: Error message if status='error'
    """
    from ..services.perplexity_client import query_perplexity
    
    prompt = f"""Fact-check this claim with authoritative sources:
    
Claim: {request}

Provide:
1. Verdict (true/false/partly true/misleading)
2. Key evidence supporting or refuting the claim
3. Context and nuance
4. Cite all authoritative sources (scientific journals, government data, expert statements)"""
    
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


__all__ = ["lookup_fact_checks", "research_fact_with_perplexity"]
