"""Example usage of the news verification agent v2."""

from __future__ import annotations

import os
import uuid
from dotenv import load_dotenv

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import the root agent
from news_info_verification_v2 import root_agent


# Constants
APP_NAME = "news_verification_v2"
USER_ID = "test_user"


def main():
    """Run the news verification agent with example queries."""
    
    # Load environment variables
    load_dotenv()
    
    # Verify API keys are set
    required_keys = ["GOOGLE_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print(f"❌ Missing required API keys: {', '.join(missing_keys)}")
        print("\nPlease set in .env file:")
        for key in missing_keys:
            print(f"  {key}=your_key_here")
        return
    
    # Optional but recommended API keys
    optional_keys = [
        "GNEWS_API_KEY",
        "FACTCHECK_API_KEY", 
        "VIRUSTOTAL_API_KEY",
        "PERPLEXITY_API_KEY",
    ]
    missing_optional = [key for key in optional_keys if not os.getenv(key)]
    
    if missing_optional:
        print(f"⚠️  Optional API keys not set (some features may be limited):")
        for key in missing_optional:
            print(f"   - {key}")
        print()
    
    # Create agent
    print("🤖 Initializing News Verification Agent v2...\n")
    
    # Create session service
    session_service = InMemorySessionService()
    
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}\n")
    
    # Create runner (will auto-create session on first use)
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service
    )
    
    # Example queries
    examples = [
        "Is it true that drinking coffee reduces the risk of cancer?",
        "Check this news: New study shows climate change is accelerating faster than predicted",
        "Is this a scam? Urgent: Your account will be suspended unless you verify your identity immediately at http://suspicious-link.com",
    ]
    
    print("=" * 80)
    print("Example Queries")
    print("=" * 80)
    
    for i, query in enumerate(examples, 1):
        print(f"\n[{i}] {query}")
    
    print("\n" + "=" * 80)
    print("Select a query (1-3) or enter your own:")
    print("=" * 80)
    
    user_input = input("\n> ").strip()
    
    # Determine query
    if user_input in ["1", "2", "3"]:
        query = examples[int(user_input) - 1]
    elif user_input:
        query = user_input
    else:
        print("❌ No query provided. Exiting.")
        return
    
    # Execute verification
    print(f"\n🔍 Verifying: {query}\n")
    print("⏳ This may take 30-60 seconds as we query multiple APIs...\n")
    
    try:
        # Create message content
        new_message = types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )
        
        # Run agent and collect response
        final_response = None
        for event in runner.run(
            user_id=USER_ID,
            session_id=session_id,
            new_message=new_message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                    break
        
        if final_response:
            print("=" * 80)
            print("VERIFICATION REPORT")
            print("=" * 80)
            print()
            print(final_response)
            print()
            print("=" * 80)
        else:
            print("❌ No response generated from agent")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        print("\nTroubleshooting:")
        print("1. Check that all API keys are correctly set")
        print("2. Verify your internet connection")
        print("3. Check API rate limits")
        print("4. Review error message above for specific issues")


if __name__ == "__main__":
    main()
