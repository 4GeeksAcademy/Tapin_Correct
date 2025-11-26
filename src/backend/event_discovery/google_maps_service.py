import os
import requests


def fetch_google_events(city="Houston", radius_m=10000, limit=20):
    """Fetch nearby places from Google Maps Places API and return simplified event-like objects.

    This is intentionally lightweight — Google Places is not an events API, so results are "places"
    that could represent events (venues, bars, community centers). Use this as a fallback/augmentation
    for Ticketmaster results.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return []

    try:
        # Resolve city -> lat/lng
        geo_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geo_params = {"address": city, "key": api_key}
        geo_resp = requests.get(geo_url, params=geo_params, timeout=5)
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            return []
        loc = geo_data["results"][0]["geometry"]["location"]
        latlng = f"{loc['lat']},{loc['lng']}"

        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places_params = {
            "location": latlng,
            "radius": radius_m,
            "keyword": "event|concert|meetup|festival",
            "key": api_key,
        }
        places_resp = requests.get(places_url, params=places_params, timeout=5)
        places = places_resp.json()

        out = []
        for p in places.get("results", [])[:limit]:
            out.append(
                {
                    "id": p.get("place_id"),
                    "title": p.get("name", "Untitled"),
                    "date": "TBD",
                    "time": "",
                    "location": p.get("vicinity") or p.get("name"),
                    "address": p.get("vicinity") or "",
                    "city": city,
                    "image": None,
                    "category": (
                        p.get("types", ["google_place"])[0]
                        if p.get("types")
                        else "google_place"
                    ),
                    "source": "google",
                    "url": f"https://www.google.com/maps/place/?q=place_id:{p.get('place_id')}",
                    "lat": float(p["geometry"]["location"]["lat"]),
                    "lng": float(p["geometry"]["location"]["lng"]),
                }
            )

        return out
    except Exception as e:
        # Keep errors silent for production-grade endpoint (logged upstream)
        print("Google fetch error:", e)
        return []
