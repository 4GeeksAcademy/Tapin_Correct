import os
import requests
from datetime import datetime

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")


def fetch_ticketmaster_events(location="Houston", keyword=None, limit=20):
    """
    Fetches events from Ticketmaster API and returns a standardized list.
    """
    if not TICKETMASTER_API_KEY:
        print("Warning: TICKETMASTER_API_KEY not set.")
        return []

    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    city_name = location.split(",")[0].strip() if location else ""
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": city_name,
        "size": limit,
        "sort": "date,asc",
        "classificationName": "music,arts,theatre,sports",
    }

    if keyword:
        params["keyword"] = keyword

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()

        events = []
        if "_embedded" in data and "events" in data["_embedded"]:
            for event in data["_embedded"]["events"]:
                # Extract highest resolution image
                image_url = ""
                if "images" in event and event["images"]:
                    images = sorted(
                        event["images"], key=lambda x: x.get("width", 0), reverse=True
                    )
                    image_url = images[0].get("url", "") if images else ""

                venue = (
                    event["_embedded"]["venues"][0]["name"]
                    if "_embedded" in event
                    and "venues" in event["_embedded"]
                    and event["_embedded"]["venues"]
                    else "Unknown Venue"
                )

                lat = None
                lng = None
                try:
                    if (
                        "_embedded" in event
                        and "venues" in event["_embedded"]
                        and event["_embedded"]["venues"]
                        and "location" in event["_embedded"]["venues"][0]
                    ):
                        lat = float(
                            event["_embedded"]["venues"][0]["location"].get("latitude")
                        )
                        lng = float(
                            event["_embedded"]["venues"][0]["location"].get("longitude")
                        )
                except Exception:
                    lat = None
                    lng = None

                category = "Event"
                try:
                    if "classifications" in event and event["classifications"]:
                        category = (
                            event["classifications"][0]
                            .get("segment", {})
                            .get("name", "Event")
                        )
                except Exception:
                    category = "Event"

                events.append(
                    {
                        "id": event.get("id"),
                        "title": event.get("name"),
                        "date": event.get("dates", {})
                        .get("start", {})
                        .get("localDate"),
                        "time": event.get("dates", {})
                        .get("start", {})
                        .get("localTime", "TBD"),
                        "location": venue,
                        "city": city_name,
                        "image": image_url,
                        "category": category,
                        "source": "ticketmaster",
                        "url": event.get("url"),
                        "lat": lat,
                        "lng": lng,
                    }
                )

        return events
    except Exception as e:
        print(f"Error fetching Ticketmaster events: {e}")
        return []
