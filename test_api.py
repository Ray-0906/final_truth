"""Test script for calling the news verification agent via API."""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:8000"
APP_NAME = "news_info_verification_v2"
USER_ID = "test_user"

def create_session():
    """Create a new session."""
    url = f"{BASE_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions"
    response = requests.post(url)
    response.raise_for_status()
    return response.json()

def send_message_sse(session_id: str, message: str):
    """Send a message to the agent via SSE endpoint."""
    url = f"{BASE_URL}/run_sse"
    payload = {
        "app_name": APP_NAME,
        "user_id": USER_ID,
        "session_id": session_id,
        "new_message": {
            "parts": [{"text": message}],
            "role": "user"
        }
    }
    
    # SSE returns streaming response
    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()
    
    # Parse SSE events
    events = []
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    event_data = json.loads(line_str[6:])
                    events.append(event_data)
                except json.JSONDecodeError:
                    continue
    
    return events

def get_session_state(session_id: str):
    """Get the current session state."""
    url = f"{BASE_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions/{session_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def main():
    print("🚀 Starting News Verification API Test\n")
    
    # Step 1: Create session
    print("1. Creating session...")
    session = create_session()
    session_id = session["id"]
    print(f"✅ Session created: {session_id}\n")
    
    # Step 2: Send claim for verification
    claim = "woman died at Makanagudem village in Konaseema district of Andhra Pradesh as a palmyra tree fell on her due to gales"
    print(f"2. Verifying claim:\n   {claim}\n")
    print("⏳ Processing (this may take 30-60 seconds)...\n")
    
    events = send_message_sse(session_id, claim)
    print(f"✅ Received {len(events)} events\n")
    
    # Step 3: Extract final report from last event
    final_report = None
    for event in reversed(events):
        if event.get("content") and event["content"].get("parts"):
            for part in event["content"]["parts"]:
                if "text" in part and len(part["text"]) > 100:
                    final_report = part["text"]
                    break
        if final_report:
            break
    
    if final_report:
        print("=" * 80)
        print("VERIFICATION REPORT")
        print("=" * 80)
        print(final_report)
        print("=" * 80)
    else:
        print("⚠️ No final report found in response")
        print(f"Last event: {events[-1] if events else 'No events'}")
    
    # Step 4: Get session state
    print("\n3. Fetching session state...")
    state = get_session_state(session_id)
    state_keys = list(state.get('state', {}).keys())
    print(f"✅ State keys: {state_keys}")
    
    if 'final_report' in state.get('state', {}):
        print("\n📊 Final report stored in state!")
    
    print("\n✨ Test completed!")

if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
