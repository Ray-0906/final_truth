"""Simple API example using /run endpoint (non-streaming)."""

import requests
import json

# 1. Create a session first
session_response = requests.post(
    "http://localhost:8000/apps/news_info_verification_v2/users/user123/sessions"
)
session_id = session_response.json()["id"]
print(f"Session ID: {session_id}")

# 2. Send your claim via the /run endpoint (non-streaming)
claim = "woman died at Makanagudem village in Konaseema district"

print(f"\nVerifying claim: {claim}")
print("Processing (this may take 30-60 seconds)...\n")

response = requests.post(
    "http://localhost:8000/run",
    json={
        "app_name": "news_info_verification_v2",
        "user_id": "user123",
        "session_id": session_id,
        "new_message": {
            "parts": [{"text": claim}],
            "role": "user"
        }
    }
)

# 3. Parse the response
result = response.json()

# Extract the final text from the response
final_report = ""
if result.get("content") and result["content"].get("parts"):
    for part in result["content"]["parts"]:
        if "text" in part:
            text = part["text"]
            # Prefer text with "# Verification Report" if available
            if "# Verification Report" in text:
                final_report = text
                break
            elif len(text) > len(final_report):
                final_report = text

print("="*80)
print("VERIFICATION REPORT")
print("="*80)
print(final_report if final_report else "No report generated")
print("="*80)

# Optional: Show session state
print("\n📊 Session State Keys:", list(result.get("state", {}).keys()))
