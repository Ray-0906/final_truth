"""Simple API example - just the essential call."""

import requests
import json

# 1. Create a session first
session_response = requests.post(
    "http://localhost:8000/apps/news_info_verification_v2/users/user123/sessions"
)
session_id = session_response.json()["id"]
print(f"Session ID: {session_id}")

# 2. Send your claim via the /run_sse endpoint
claim = "woman died at Makanagudem village in Konaseema district"

response = requests.post(
    "http://localhost:8000/run_sse",
    json={
        "app_name": "news_info_verification_v2",
        "user_id": "user123",
        "session_id": session_id,
        "new_message": {
            "parts": [{"text": claim}],
            "role": "user"
        }
    },
    stream=True
)

# 3. Read the streaming response
print("\nProcessing...")
events = []
for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            try:
                event = json.loads(line_str[6:])
                events.append(event)
                print(".", end="", flush=True)
            except:
                pass

# Find the final report from the last event with substantial text
final_report = ""
for event in reversed(events):
    if event.get("content") and event["content"].get("parts"):
        for part in event["content"]["parts"]:
            # Look for text that starts with "# Verification Report" (the final report)
            if "text" in part and "# Verification Report" in part["text"]:
                final_report = part["text"]
                break
        if final_report:
            break

# If no formatted report found, get the longest text response
if not final_report:
    for event in reversed(events):
        if event.get("content") and event["content"].get("parts"):
            for part in event["content"]["parts"]:
                if "text" in part and len(part["text"]) > len(final_report):
                    final_report = part["text"]

print("\n\n" + "="*80)
print("VERIFICATION REPORT")
print("="*80)
print(final_report if final_report else "No report generated")
print("="*80)
