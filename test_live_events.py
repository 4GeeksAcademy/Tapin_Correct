#!/usr/bin/env python3
"""
Quick test script to verify live events endpoint works correctly.
Tests the Ticketmaster service integration.
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend'))

from backend.event_discovery.ticketmaster_service import fetch_ticketmaster_events

print("=" * 60)
print("Testing Live Events Integration")
print("=" * 60)

# Test Ticketmaster service
print("\n1. Testing Ticketmaster Service...")
print("-" * 60)

api_key = os.getenv("TICKETMASTER_API_KEY")
if not api_key:
    print("❌ TICKETMASTER_API_KEY not set in environment")
    print("   Set it with: export TICKETMASTER_API_KEY='your-key-here'")
else:
    print(f"✅ API Key found: {api_key[:10]}...")

print("\nFetching events for Houston, TX...")
events = fetch_ticketmaster_events(city="Houston, TX", limit=5)

print(f"\n✅ Fetched {len(events)} events")

if events:
    print("\n📋 Sample Event:")
    print("-" * 60)
    event = events[0]
    for key, value in event.items():
        print(f"{key:15}: {value}")

    print("\n✅ All events have required fields:")
    required_fields = ['id', 'title', 'date', 'location', 'city', 'source', 'lat', 'lng']
    for field in required_fields:
        has_field = all(field in e for e in events)
        status = "✅" if has_field else "❌"
        print(f"  {status} {field}")
else:
    print("⚠️  No events returned. Check:")
    print("   1. TICKETMASTER_API_KEY is valid")
    print("   2. API key has not exceeded rate limits")
    print("   3. Network connection is working")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
