"""Google Fact Check Tools API client."""

import os

import requests
from dotenv import load_dotenv


load_dotenv()
FACTCHECK_API_KEY = os.getenv("FACTCHECK_API_KEY", "")
FACTCHECK_BASE_URL = "https://factchecktools.googleapis.com/v1alpha1"


def search_fact_checks(query: str, max_results: int = 10) -> list:
    """
    Search for fact-checks using Google Fact Check Tools API.
    
    Args:
        query: Claim to search for
        max_results: Maximum number of results (default 10)
        
    Returns:
        List of fact-check dicts with keys: claim, claimant, rating, url, source
        
    Raises:
        ValueError: If API key is not configured
        requests.HTTPError: If API request fails
    """
    if not FACTCHECK_API_KEY:
        raise ValueError("FACTCHECK_API_KEY environment variable not set")
    
    params = {
        "query": query,
        "key": FACTCHECK_API_KEY,
        "pageSize": min(max_results, 10),
        "languageCode": "en",
    }
    
    response = requests.get(
        f"{FACTCHECK_BASE_URL}/claims:search",
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    
    data = response.json()
    claims = data.get("claims", [])
    
    # Normalize response format
    results = []
    for claim_item in claims:
        claim_text = claim_item.get("text", "")
        claimant = claim_item.get("claimant", "Unknown")
        
        # Each claim can have multiple reviews
        for review in claim_item.get("claimReview", []):
            results.append({
                "claim": claim_text,
                "claimant": claimant,
                "rating": review.get("textualRating", "Unknown"),
                "url": review.get("url", ""),
                "source": review.get("publisher", {}).get("name", "Unknown"),
                "title": review.get("title", ""),
            })
    
    return results[:max_results]


__all__ = ["search_fact_checks"]
