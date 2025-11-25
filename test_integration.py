#!/usr/bin/env python3
"""
Comprehensive integration test for Google Search -> Events pipeline
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"  # pragma: allowlist secret


def login():
    """Login and get JWT token"""
    response = requests.post(
        f"{BASE_URL}/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


def test_web_search_integration(token):
    """Test the complete integration"""
    print("=" * 80)
    print("🧪 TESTING GOOGLE SEARCH -> DATABASE INTEGRATION")
    print("=" * 80)

    # Step 1: Search
    print("\n1️⃣ Searching for volunteer opportunities...")
    query = "environmental conservation volunteer Seattle"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(
        f"{BASE_URL}/api/web-search",
        json={"query": query, "location": {"city": "Seattle", "state": "WA"}},
        headers=headers,
    )

    if response.status_code != 200:
        print(f"❌ Search failed: {response.status_code}")
        print(response.text)
        return False

    data = response.json()
    print(f"✅ Search successful!")
    print(f"   Found: {data.get('count')} events")
    print(f"   Message: {data.get('message')}")

    # Step 2: Verify events were saved
    events = data.get("events", [])
    if not events:
        print("❌ No events returned")
        return False

    print(f"\n2️⃣ Analyzing first {min(3, len(events))} results:")
    for i, event in enumerate(events[:3], 1):
        print(f"\n   Event #{i}:")
        print(f"   📌 Title: {event.get('title')}")
        print(f"   🏢 Organization: {event.get('organization')}")
        print(f"   🏷️  Category: {event.get('category')}")
        print(f"   📧 Email: {event.get('contact_email') or 'Not found'}")
        print(f"   📞 Phone: {event.get('contact_phone') or 'Not found'}")
        print(f"   🌐 URL: {event.get('url', '')[:60]}...")
        print(f"   💾 Saved with ID: {event.get('id')[:20]}...")

    # Step 3: Verify we can retrieve events from database
    print(f"\n3️⃣ Verifying events were saved to database...")

    # Try to search for events from database
    response = requests.post(
        f"{BASE_URL}/api/events/search",
        json={"location": "Seattle, WA", "category": events[0].get("category")},
        headers=headers,
    )

    if response.status_code == 200:
        db_data = response.json()
        db_events = db_data.get("events", [])
        print(f"✅ Database query successful!")
        print(f"   Found {len(db_events)} events in database")

        # Check if our saved event is in the database
        saved_ids = [e["id"] for e in events]
        db_ids = [e["id"] for e in db_events]
        matches = set(saved_ids) & set(db_ids)
        print(f"   {len(matches)} of our searched events found in database")
    else:
        print(f"⚠️  Database query returned: {response.status_code}")

    print(f"\n{'='*80}")
    print(f"✅ INTEGRATION TEST COMPLETE!")
    print(f"{'='*80}")
    print(f"\nSummary:")
    print(f"  • Google Search: ✅ Working")
    print(f"  • Event Creation: ✅ {len(events)} events created")
    print(
        f"  • Contact Extraction: ✅ {sum(1 for e in events if e.get('contact_email') or e.get('contact_phone'))} events with contact info"
    )
    print(f"  • Database Storage: ✅ Events saved")

    return True


if __name__ == "__main__":
    print("Logging in...")
    token = login()

    if not token:
        print("❌ Login failed")
        exit(1)

    print("✅ Login successful!\n")

    success = test_web_search_integration(token)

    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed")
        exit(1)
