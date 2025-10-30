"""Perplexity API client for AI-powered research."""

import os

import requests
from dotenv import load_dotenv


load_dotenv()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"


def query_perplexity(prompt: str, model: str = "sonar") -> dict:
    """
    Query Perplexity AI for web research.
    
    Args:
        prompt: Research query or question
        model: Perplexity model to use (default: sonar)
        
    Returns:
        dict with keys:
            - answer: Perplexity's response text
            - citations: List of source URLs
            - model: Model used
            
    Raises:
        ValueError: If API key is not configured
        requests.HTTPError: If API request fails
    """
    if not PERPLEXITY_API_KEY:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set")
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    
    try:
        response = requests.post(
            f"{PERPLEXITY_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
    except requests.HTTPError as e:
        # Include response body in error for debugging
        error_msg = str(e)
        try:
            error_detail = response.json()
            error_msg = f"{e}. API Response: {error_detail}"
        except:
            pass
        raise requests.HTTPError(error_msg) from e
    
    data = response.json()
    
    # Extract answer and citations
    choices = data.get("choices", [])
    answer = ""
    if choices:
        answer = choices[0].get("message", {}).get("content", "")
    
    citations = data.get("citations", [])
    
    return {
        "answer": answer,
        "citations": citations,
        "model": model,
    }


__all__ = ["query_perplexity"]
