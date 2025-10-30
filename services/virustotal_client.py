"""VirusTotal API client for URL security scanning."""

import os
import time

import requests
from dotenv import load_dotenv


load_dotenv()
VIRUSTOTAL_API_KEY = os.getenv("VT_API_KEY", "")  # Match .env variable name
VIRUSTOTAL_BASE_URL = "https://www.virustotal.com/api/v3"


def scan_url(url: str, wait_for_result: bool = True) -> dict:
    """
    Scan a URL using VirusTotal API.
    
    Args:
        url: URL to scan
        wait_for_result: If True, wait for scan completion (default)
        
    Returns:
        dict with keys:
            - url: Original URL
            - malicious_count: Number of vendors flagging as malicious
            - total_scanners: Total number of vendors
            - analysis_url: VirusTotal analysis page URL
            - status: 'malicious', 'suspicious', or 'clean'
            
    Raises:
        ValueError: If API key is not configured
        requests.HTTPError: If API request fails
    """
    if not VIRUSTOTAL_API_KEY:
        raise ValueError("VT_API_KEY environment variable not set")
    
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY,
    }
    
    # Submit URL for scanning
    response = requests.post(
        f"{VIRUSTOTAL_BASE_URL}/urls",
        headers=headers,
        data={"url": url},
        timeout=10,
    )
    response.raise_for_status()
    
    scan_data = response.json()
    analysis_id = scan_data.get("data", {}).get("id", "")
    
    if not wait_for_result:
        return {
            "url": url,
            "status": "pending",
            "analysis_id": analysis_id,
        }
    
    # Wait for analysis to complete (max 30 seconds)
    for _ in range(6):
        time.sleep(5)
        
        analysis_response = requests.get(
            f"{VIRUSTOTAL_BASE_URL}/analyses/{analysis_id}",
            headers=headers,
            timeout=10,
        )
        analysis_response.raise_for_status()
        
        analysis_data = analysis_response.json()
        status = analysis_data.get("data", {}).get("attributes", {}).get("status", "")
        
        if status == "completed":
            break
    
    # Get analysis results
    stats = analysis_data.get("data", {}).get("attributes", {}).get("stats", {})
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    total = sum(stats.values()) if stats else 1
    
    # Determine overall status
    if malicious > 0:
        verdict = "malicious"
    elif suspicious > 0:
        verdict = "suspicious"
    else:
        verdict = "clean"
    
    return {
        "url": url,
        "malicious_count": malicious,
        "suspicious_count": suspicious,
        "total_scanners": total,
        "analysis_url": f"https://www.virustotal.com/gui/url/{analysis_id}",
        "status": verdict,
    }


__all__ = ["scan_url"]
