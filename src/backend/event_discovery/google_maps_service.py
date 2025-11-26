import os
import requests


def fetch_google_events(city="Houston", radius_m=10000, limit=20):
    """Fetch events using Google Custom Search Engine API.

    Uses Google CSE to search for events in the specified city.
    This is more event-focused than Google Places API.
    """
    api_key = os.getenv("CUSTOM_SEARCH_API_KEY") or os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        print(
            "🔴 WARNING: Google Custom Search API key or Engine ID not set. Skipping fetch."
        )
        return []

    try:
        # Build search query for events in the city
        query = f"events in {city} concerts festivals shows"
        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": min(limit, 10),  # CSE API max is 10 per request
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        events = []
        for idx, item in enumerate(data.get("items", [])):
            # Extract structured data if available
            page_map = item.get("pagemap", {})
            metatags = (
                page_map.get("metatags", [{}])[0] if page_map.get("metatags") else {}
            )

            # Try to extract event details
            title = item.get("title", "Untitled Event")
            snippet = item.get("snippet", "")
            link = item.get("link", "")

            # Try to extract image
            image = None
            if page_map.get("cse_image"):
                image = page_map["cse_image"][0].get("src")
            elif metatags.get("og:image"):
                image = metatags.get("og:image")

            events.append(
                {
                    "id": f"google_cse_{idx}_{hash(link)}",
                    "title": title,
                    "description": snippet,
                    "date": "TBD",  # CSE doesn't provide structured dates
                    "time": "",
                    "location": city,
                    "city": city.split(",")[0].strip(),
                    "image": image,
                    "category": "Event",
                    "source": "google_search",
                    "url": link,
                    "lat": 0.0,  # CSE doesn't provide coordinates
                    "lng": 0.0,
                }
            )

        print(
            f"✅ Successfully fetched {len(events)} Google Custom Search events for {city}"
        )
        return events

    except requests.exceptions.RequestException as e:
        print(f"🔴 GOOGLE CUSTOM SEARCH API ERROR: {e}")
        return []
    except Exception as e:
        print(f"🔴 Error processing Google Custom Search data: {e}")
        return []
