#!/usr/bin/env python3
"""
Test script for the /api/web-search endpoint
"""
import requests
import json

# Backend URL
BASE_URL = "http://127.0.0.1:5000"

# Test credentials (you may need to adjust these)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"  # pragma: allowlist secret


def login():
    """Login and get JWT token"""
    print("Logging in...")
    response = requests.post(
        f"{BASE_URL}/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.json())
        return None


def test_web_search(token):
    """Test the /api/web-search endpoint"""
    print("\n" + "=" * 80)
    print("Testing /api/web-search endpoint")
    print("=" * 80)

    query = "animal shelter volunteer San Francisco"
    print(f"\nSearching for: '{query}'")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(
        f"{BASE_URL}/api/web-search", json={"query": query}, headers=headers
    )

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS!")
        print(f"\nResults: {data.get('count')} found")
        print(f"Source: {data.get('source')}")

        results = data.get("results", [])
        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. [{result.get('category')}] {result.get('title')}")
            snippet = result.get("snippet", "")[:100]
            print(f"   {snippet}...")
            print(f"   {result.get('link')}")

        if len(results) > 3:
            print(f"\n... and {len(results) - 3} more results")

        return True
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(response.json())
        return False


if __name__ == "__main__":
    # Try to login
    token = login()

    if token:
        # Test the web search endpoint
        test_web_search(token)
    else:
        print("\n⚠️  Could not test web search - login required")
        print("You may need to create a test user first or update credentials")
