"""GNews API client for fetching licensed news articles."""

import os

import requests
from dotenv import load_dotenv


load_dotenv()
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
GNEWS_BASE_URL = "https://gnews.io/api/v4"


def search_news(query: str, max_results: int = 10) -> list:
    """
    Search for news articles using GNews API.
    
    Args:
        query: Search query string
        max_results: Maximum number of articles to return (default 10)
        
    Returns:
        List of article dicts with keys: title, url, source, published_date, description
        
    Raises:
        ValueError: If API key is not configured
        requests.HTTPError: If API request fails
    """
    if not GNEWS_API_KEY:
        raise ValueError("GNEWS_API_KEY environment variable not set")
    
    # GNews query preprocessing:
    # 1. Remove commas and special chars (causes syntax errors)
    # 2. Limit to 200 chars max
    # 3. Filter out short/filler words
    
    # Clean special characters that break GNews syntax
    query = query.replace(',', ' ').replace(';', ' ').replace(':', ' ')
    query = ' '.join(query.split())  # Normalize whitespace
    
    # Truncate if needed
    if len(query) > 200:
        words = query[:150].split()
        filtered = [w for w in words if len(w) > 3 and w.lower() not in 
                   {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'said', 'told'}]
        query = ' '.join(filtered[:15])
    
    params = {
        "q": query,
        "token": GNEWS_API_KEY,
        "lang": "en",
        "max": min(max_results, 10),  # API limit
        "sortby": "relevance",
    }
    
    try:
        response = requests.get(
            f"{GNEWS_BASE_URL}/search",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
    except requests.HTTPError as e:
        # Include response body for debugging
        error_msg = str(e)
        try:
            error_detail = response.json()
            error_msg = f"{e}. API Response: {error_detail}"
        except:
            pass
        raise requests.HTTPError(error_msg) from e
    
    data = response.json()
    articles = data.get("articles", [])
    
    # Normalize response format
    return [
        {
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "source": article.get("source", {}).get("name", "Unknown"),
            "published_date": article.get("publishedAt", ""),
            "description": article.get("description", ""),
        }
        for article in articles
    ]


__all__ = ["search_news"]
