#!/usr/bin/env python3
"""
Diagnostic script for Google Custom Search API setup.
"""
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def diagnose():
    """Run diagnostics on Google API setup."""
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

    print("=" * 80)
    print("Google Custom Search API Diagnostics")
    print("=" * 80)

    # Check environment variables
    print("\n1. Environment Variables:")
    print(f"   GOOGLE_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    if api_key:
        print(f"      Value: {api_key[:20]}...{api_key[-4:]}")
    print(
        f"   CUSTOM_SEARCH_ENGINE_ID: {'✅ Set' if search_engine_id else '❌ Not set'}"
    )
    if search_engine_id:
        print(f"      Value: {search_engine_id}")

    if not api_key or not search_engine_id:
        print("\n❌ Missing required environment variables!")
        return

    # Try to build the service
    print("\n2. Building Custom Search Service:")
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        print("   ✅ Service built successfully")
    except Exception as e:
        print(f"   ❌ Failed to build service: {e}")
        return

    # Try a simple search
    print("\n3. Testing Search Query:")
    try:
        result = service.cse().list(q="test", cx=search_engine_id, num=1).execute()

        print("   ✅ Search successful!")
        print(
            f"   Found {result.get('searchInformation', {}).get('totalResults', 0)} total results"
        )

        items = result.get("items", [])
        if items:
            print(f"\n   Sample result:")
            print(f"   Title: {items[0].get('title', 'N/A')}")
            print(f"   Link: {items[0].get('link', 'N/A')}")

    except HttpError as e:
        print(f"   ❌ HTTP Error {e.resp.status}: {e.error_details}")
        print("\n   Common causes:")
        print("   • Custom Search API not enabled in Google Cloud Console")
        print("   • Billing not enabled on the project")
        print("   • API key doesn't have permission for Custom Search API")
        print("   • API key restrictions blocking Custom Search API")
        print("\n   Next steps:")
        print(
            "   1. Go to: https://console.cloud.google.com/apis/library/customsearch.googleapis.com"
        )
        print("   2. Make sure you're in the correct project")
        print("   3. Click 'Enable' if the API is not enabled")
        print("   4. Enable billing: https://console.cloud.google.com/billing")
        print(
            "   5. Check API key restrictions: https://console.cloud.google.com/apis/credentials"
        )

    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    diagnose()
