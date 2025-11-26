import os
import requests
from datetime import datetime


def fetch_ticketmaster_events(city="Houston", keyword=None, limit=20):
    """
    Fetches events from Ticketmaster API and returns a standardized list.
    More robust version with better error handling and data validation.
    """
    api_key = os.getenv("TICKETMASTER_API_KEY")
    if not api_key:
        print("🔴 WARNING: TICKETMASTER_API_KEY is not set. Skipping fetch.")
        return []

    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": api_key,
        "city": city.split(",")[0].strip(),
        "size": limit,
        "sort": "date,asc",
        "classificationName": "Music,Sports,Arts & Theatre,Film,Miscellaneous",
    }
    if keyword:
        params["keyword"] = keyword

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        events = []
        for event in data.get("_embedded", {}).get("events", []):
            # Get 16:9 ratio image for better display
            image = next(
                (img for img in event.get("images", []) if img.get("ratio") == "16_9"),
                None,
            )
            venue = event.get("_embedded", {}).get("venues", [{}])[0]

            # Skip events without essential data for a cleaner demo
            if not venue.get("location"):
                continue

            events.append(
                {
                    "id": event["id"],
                    "title": event["name"],
                    "date": event.get("dates", {}).get("start", {}).get("localDate"),
                    "time": event.get("dates", {})
                    .get("start", {})
                    .get("localTime", ""),
                    "location": venue.get("name", "TBA"),
                    "city": venue.get("city", {}).get(
                        "name", city.split(",")[0].strip()
                    ),
                    "image": image["url"] if image else None,
                    "category": (
                        event.get("classifications", [{}])[0].get("segment", {}) or {}
                    ).get("name", "Event"),
                    "source": "ticketmaster",
                    "url": event.get("url"),
                    "lat": float(venue["location"]["latitude"]),
                    "lng": float(venue["location"]["longitude"]),
                }
            )

        print(f"✅ Successfully fetched {len(events)} Ticketmaster events for {city}")
        return events

    except requests.exceptions.RequestException as e:
        print(f"🔴 TICKETMASTER API ERROR: {e}")
        return []
    except Exception as e:
        print(f"🔴 Error processing Ticketmaster data: {e}")
        return []
