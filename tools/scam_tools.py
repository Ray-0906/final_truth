"""Scam detection tool functions."""

import re


def scan_urls_with_virustotal(request: str) -> dict:
    """
    Scan URLs for malicious content using VirusTotal API.
    
    Args:
        request: Text containing URLs to scan
        
    Returns:
        dict with:
            - status: 'success' or 'error'
            - results: List of {url, malicious_count, total_scanners, analysis_url} dicts
            - error: Error message if status='error'
    """
    from ..services.virustotal_client import scan_url
    
    # Extract URLs from request
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, request)
    
    if not urls:
        return {
            "status": "success",
            "results": [],
            "message": "No URLs found in request",
        }
    
    try:
        results = []
        for url in urls:
            scan_result = scan_url(url)
            results.append(scan_result)
        
        return {
            "status": "success",
            "results": results,
            "scanned_count": len(results),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "urls_attempted": urls,
        }


def research_scam_with_perplexity(request: str) -> dict:
    """
    Research potential scams using Perplexity AI's web search.
    
    Args:
        request: Description of potential scam
        
    Returns:
        dict with:
            - status: 'success' or 'error'
            - answer: Perplexity's research findings
            - citations: List of source URLs
            - error: Error message if status='error'
    """
    from ..services.perplexity_client import query_perplexity
    
    prompt = f"""Analyze this potential scam and search for related reports:
    
Content: {request}

Provide:
1. Is this a known scam pattern?
2. Similar scam reports or warnings
3. Legitimate context (if it's NOT a scam)
4. Red flags or warning signs
5. Cite all sources (scam databases, consumer protection agencies, news reports)"""
    
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


def analyze_scam_sentiment(request: str) -> dict:
    """
    Analyze text for scam manipulation tactics using LLM.
    
    Args:
        request: Text to analyze for scam indicators
        
    Returns:
        dict with:
            - status: 'success' or 'error'
            - tactics: List of manipulation tactics detected
            - urgency_score: 0.0-1.0 (how urgent/pressuring)
            - red_flags: List of specific red flag phrases
            - error: Error message if status='error'
    """
    try:
        # Local analysis without external API
        tactics = []
        red_flags = []
        urgency_score = 0.0
        
        text_lower = request.lower()
        
        # Urgency tactics
        urgency_phrases = [
            "act now", "limited time", "expires soon", "urgent",
            "immediate action", "don't wait", "hurry", "right now",
            "within 24 hours", "before it's too late",
        ]
        urgency_count = sum(1 for phrase in urgency_phrases if phrase in text_lower)
        if urgency_count > 0:
            tactics.append("Artificial Urgency")
            urgency_score = min(1.0, urgency_count * 0.25)
            red_flags.extend([p for p in urgency_phrases if p in text_lower])
        
        # Authority impersonation
        authority_phrases = [
            "irs", "government", "bank", "official notice",
            "legal action", "warrant", "suspend your account",
            "verify your identity", "security alert",
        ]
        if any(phrase in text_lower for phrase in authority_phrases):
            tactics.append("Authority Impersonation")
            red_flags.extend([p for p in authority_phrases if p in text_lower])
        
        # Financial pressure
        financial_phrases = [
            "send money", "wire transfer", "gift card", "bitcoin",
            "confirm payment", "refund", "tax refund", "prize",
            "won the lottery", "inheritance", "investment opportunity",
        ]
        if any(phrase in text_lower for phrase in financial_phrases):
            tactics.append("Financial Manipulation")
            red_flags.extend([p for p in financial_phrases if p in text_lower])
        
        # Threatening language
        threat_phrases = [
            "arrest", "jail", "lawsuit", "legal consequences",
            "suspended", "terminated", "penalty", "fine",
        ]
        if any(phrase in text_lower for phrase in threat_phrases):
            tactics.append("Threatening Language")
            red_flags.extend([p for p in threat_phrases if p in text_lower])
        
        # Too good to be true
        too_good_phrases = [
            "guaranteed", "risk-free", "100% profit", "make money fast",
            "work from home", "easy money", "no experience needed",
        ]
        if any(phrase in text_lower for phrase in too_good_phrases):
            tactics.append("Too Good To Be True")
            red_flags.extend([p for p in too_good_phrases if p in text_lower])
        
        return {
            "status": "success",
            "tactics": tactics,
            "urgency_score": round(urgency_score, 2),
            "red_flags": list(set(red_flags)),  # dedupe
            "analysis_confidence": 0.8 if tactics else 0.5,
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


__all__ = [
    "scan_urls_with_virustotal",
    "research_scam_with_perplexity",
    "analyze_scam_sentiment",
]
