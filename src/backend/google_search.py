import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
from categories import CATEGORIES

load_dotenv()


def search_events(query):
    """
    Searches for volunteer events using the Google Custom Search JSON API.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        return {"error": "Google API key or Search Engine ID not configured."}

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        result = (
            service.cse()
            .list(q=query, cx=search_engine_id, num=10)  # Number of results to return
            .execute()
        )
        items = result.get("items", [])
        return refine_and_categorize(items)
    except Exception as e:
        return {"error": str(e)}


def refine_and_categorize(items):
    """
    Refines raw Google search results and categorizes them.
    """
    refined_results = []
    for item in items:
        categorized = False
        for category in CATEGORIES:
            if (
                category.lower() in item.get("title", "").lower()
                or category.lower() in item.get("snippet", "").lower()
            ):
                item["category"] = category
                refined_results.append(item)
                categorized = True
                break
        if not categorized:
            item["category"] = "Other"
            refined_results.append(item)
    return refined_results
