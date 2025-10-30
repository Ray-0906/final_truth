"""Debug script to check session state."""

import requests
import json

# Create session and run query
session_response = requests.post(
    "http://localhost:8000/apps/news_info_verification_v2/users/debug_user/sessions"
)
session_id = session_response.json()["id"]
print(f"Session ID: {session_id}\n")

claim = "woman died at Makanagudem village"

response = requests.post(
    "http://localhost:8000/run_sse",
    json={
        "app_name": "news_info_verification_v2",
        "user_id": "debug_user",
        "session_id": session_id,
        "new_message": {
            "parts": [{"text": claim}],
            "role": "user"
        }
    },
    stream=True
)

print("Waiting for completion...")
for line in response.iter_lines():
    if line:
        print(".", end="", flush=True)

print("\n\nFetching session state...")

# Get full session state
state_response = requests.get(
    f"http://localhost:8000/apps/news_info_verification_v2/users/debug_user/sessions/{session_id}"
)
session_data = state_response.json()

print("\n" + "="*80)
print("ALL STATE KEYS:")
print("="*80)
for key, value in session_data.get("state", {}).items():
    print(f"\n--- {key} ---")
    if isinstance(value, str) and len(value) > 200:
        print(value[:200] + "...")
    else:
        print(value)
print("="*80)
