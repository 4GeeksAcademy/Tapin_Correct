#!/usr/bin/env python3
"""Test the event scraping and Gemini integration directly."""
import asyncio
import os

# Set environment variables
# Prefer reading the API key from the environment. Do not hard-code secrets in tests.
os.environ["LLM_PROVIDER"] = "gemini"
# Use an environment variable set locally or in CI secrets. If not set, tests
# will skip direct Gemini calls.
if "GEMINI_API_KEY" not in os.environ:
    print("Warning: GEMINI_API_KEY not set; Gemini calls may be disabled in this test.")

from event_discovery.cache_manager import EventCacheManager
from app import app, db

with app.app_context():
    db.create_all()

    mgr = EventCacheManager()
    print("Testing localized scrape for Austin, TX only...")

    # Test localized city-specific scrape (single location only)
    print("\n1. Testing city-specific scrape (Austin, TX)...")
    try:
        events = asyncio.run(mgr.scrape_city_events("Austin", "TX"))
        print(f"   Scraped {len(events)} events for Austin, TX")
        for e in events[:5]:
            print(f"   - {e.get('title')}")
            print(f"     City: {e.get('city')}, State: {e.get('state')}")
    except Exception as e:
        import traceback

        print(f"   Error: {e}")
        traceback.print_exc()

    # Test full search flow (localized)
    print("\n2. Testing full search flow (Austin, TX only)...")
    try:
        results = asyncio.run(mgr.search_by_location("Austin", "TX"))
        print(f"   Found {len(results)} events for Austin, TX")
        for e in results[:3]:
            print(f"   - {e.get('title')}")
    except Exception as e:
        import traceback

        print(f"   Error: {e}")
        traceback.print_exc()

    print("\nDone!")
