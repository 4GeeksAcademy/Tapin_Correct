#!/usr/bin/env python3
"""
Simple test script for Google Custom Search functionality.
"""
import sys
import os
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "backend"))

from google_search import search_events


def test_search():
    """Test the search_events function with a sample query."""
    test_query = "volunteer opportunities for animal welfare in San Francisco"

    print(f"Testing Google Custom Search with query: '{test_query}'")
    print("-" * 80)

    results = search_events(test_query)

    # Check if we got an error
    if isinstance(results, dict) and "error" in results:
        print(f"❌ ERROR: {results['error']}")
        return False

    # Display results
    if isinstance(results, list):
        print(f"✅ SUCCESS! Found {len(results)} results\n")

        for i, result in enumerate(results[:5], 1):  # Show first 5 results
            print(f"\n{i}. {result.get('title', 'No title')}")
            print(f"   Category: {result.get('category', 'Unknown')}")
            print(f"   Link: {result.get('link', 'No link')}")
            snippet = result.get("snippet", "No snippet")
            # Truncate long snippets
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
            print(f"   Snippet: {snippet}")

        if len(results) > 5:
            print(f"\n... and {len(results) - 5} more results")

        return True
    else:
        print(f"❌ Unexpected result type: {type(results)}")
        print(json.dumps(results, indent=2))
        return False


if __name__ == "__main__":
    success = test_search()
    sys.exit(0 if success else 1)
