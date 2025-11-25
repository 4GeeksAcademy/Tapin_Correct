"""Live test for Google Custom Search API with categorization."""

import os
from google_search import search_events
from dotenv import load_dotenv

load_dotenv()

print("Testing Live Google Custom Search with Categorization")
print("=" * 60)
print(f"Provider: {os.getenv('LLM_PROVIDER', 'not set')}")
print(
    f"Google API Key: {'*' * 10}{os.getenv('GOOGLE_API_KEY', '')[-4:] if os.getenv('GOOGLE_API_KEY') else 'NOT SET'}"
)
print(f"Search Engine ID: {os.getenv('CUSTOM_SEARCH_ENGINE_ID', 'NOT SET')}")
print("=" * 60)

# Test query for volunteer opportunities
query = "animal shelter volunteer opportunities Miami"
print(f"\nSearching for: '{query}'\n")

results = search_events(query)

if isinstance(results, dict) and "error" in results:
    print(f"ERROR: {results['error']}")
    print("\nTroubleshooting:")
    print("1. Ensure GOOGLE_API_KEY is set in .env")
    print("2. Ensure CUSTOM_SEARCH_ENGINE_ID is set in .env")
    print("3. Enable Custom Search API in Google Cloud Console")
    # Perplexity option removed; set LLM_PROVIDER to 'gemini' or 'ollama' if needed
    print("4. Or set LLM_PROVIDER to 'gemini' or 'ollama' to use other providers")
elif isinstance(results, list):
    print(f"Found {len(results)} results:\n")
    for i, result in enumerate(results[:5], 1):
        print(
            f"{i}. [{result.get('category', 'Other')}] {result.get('title', 'No title')}"
        )
        print(f"   {result.get('snippet', 'No snippet')[:80]}...")
        print(f"   {result.get('link', 'No link')}\n")
    print("✓ Search and categorization working successfully!")
else:
    print(f"Unexpected result type: {type(results)}")
    print(results)
