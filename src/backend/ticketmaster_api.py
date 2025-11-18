"""
Ticketmaster API Integration

Fetches real future events from Ticketmaster Discovery API
"""

import requests
from datetime import datetime, timezone
import os
from typing import List, Dict, Optional


class TicketmasterAPI:
    """Ticketmaster Discovery API client"""

    BASE_URL = "https://app.ticketmaster.com/discovery/v2"

    def __init__(self, api_key: str = None):
        """
        Initialize Ticketmaster API client.

        Args:
            api_key: Ticketmaster Consumer Key (API key)
        """
        self.api_key = api_key or os.environ.get("TICKETMASTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Ticketmaster API key required. Set TICKETMASTER_API_KEY environment variable "
                "or pass api_key parameter. Get your key at: https://developer.ticketmaster.com/"
            )

    def search_events(
        self,
        city: str = None,
        state_code: str = None,
        latitude: float = None,
        longitude: float = None,
        radius: int = 25,
        unit: str = "miles",
        size: int = 50,
        sort: str = "date,asc",
        start_date_time: str = None,
        classification_name: str = None,
    ) -> List[Dict]:
        """
        Search for events using Ticketmaster Discovery API.

        Args:
            city: City name (e.g., "Dallas")
            state_code: State code (e.g., "TX")
            latitude: Latitude for geolocation search
            longitude: Longitude for geolocation search
            radius: Search radius (default: 25)
            unit: Distance unit - "miles" or "km" (default: "miles")
            size: Number of results (max 200, default: 50)
            sort: Sort order (default: "date,asc" for future events first)
            start_date_time: Start datetime in ISO 8601 format (defaults to now for future events)
            classification_name: Filter by type (e.g., "Music", "Sports", "Arts & Theatre")

        Returns:
            List of event dictionaries in Ticketmaster format
        """
        params = {
            "apikey": self.api_key,
            "size": size,
            "sort": sort,
        }

        # Add location filters
        if city and state_code:
            params["city"] = city
            params["stateCode"] = state_code
        elif latitude and longitude:
            params["latlong"] = f"{latitude},{longitude}"
            params["radius"] = radius
            params["unit"] = unit

        # Only future events (default behavior)
        if start_date_time:
            params["startDateTime"] = start_date_time
        else:
            # Default to now for future events only
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            params["startDateTime"] = now

        # Add classification filter
        if classification_name:
            params["classificationName"] = classification_name

        try:
            response = requests.get(
                f"{self.BASE_URL}/events.json",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            # Extract events from response
            if "_embedded" in data and "events" in data["_embedded"]:
                return data["_embedded"]["events"]

            return []

        except requests.exceptions.RequestException as e:
            print(f"Ticketmaster API error: {e}")
            return []

    def convert_to_app_format(self, tm_event: Dict) -> Dict:
        """
        Convert Ticketmaster event to our app's event format.

        Args:
            tm_event: Ticketmaster event dictionary

        Returns:
            Event dictionary in our app's format
        """
        # Extract basic info
        event_id = tm_event.get("id", "")
        name = tm_event.get("name", "Untitled Event")
        url = tm_event.get("url", "")

        # Extract dates
        dates = tm_event.get("dates", {})
        start_data = dates.get("start", {})
        date_start = None
        if "dateTime" in start_data:
            date_start = start_data["dateTime"]
        elif "localDate" in start_data:
            # Has date but not time
            local_date = start_data["localDate"]
            local_time = start_data.get("localTime", "19:00:00")  # Default 7pm
            date_start = f"{local_date}T{local_time}"

        # Extract venue information
        venue_name = None
        address = None
        city = None
        state = None
        zip_code = None
        latitude = None
        longitude = None

        if "_embedded" in tm_event and "venues" in tm_event["_embedded"]:
            venues = tm_event["_embedded"]["venues"]
            if venues:
                venue = venues[0]
                venue_name = venue.get("name")

                # Location data
                if "location" in venue:
                    location = venue["location"]
                    latitude = float(location.get("latitude", 0)) if location.get("latitude") else None
                    longitude = float(location.get("longitude", 0)) if location.get("longitude") else None

                # Address data
                if "address" in venue:
                    addr = venue["address"]
                    address = addr.get("line1")

                if "city" in venue:
                    city_data = venue["city"]
                    city = city_data.get("name")

                if "state" in venue:
                    state_data = venue["state"]
                    state = state_data.get("stateCode")

                if "postalCode" in venue:
                    zip_code = venue["postalCode"]

        # Extract price information
        price_str = "Check Ticketmaster"
        if "priceRanges" in tm_event:
            price_ranges = tm_event["priceRanges"]
            if price_ranges:
                min_price = price_ranges[0].get("min")
                max_price = price_ranges[0].get("max")
                currency = price_ranges[0].get("currency", "USD")

                if min_price and max_price:
                    price_str = f"${min_price:.0f} - ${max_price:.0f} {currency}"
                elif min_price:
                    price_str = f"From ${min_price:.0f} {currency}"

        # Extract images
        image_url = None
        image_urls = []
        if "images" in tm_event:
            images = tm_event["images"]
            if images:
                # Get highest resolution image
                image_url = images[0].get("url")
                image_urls = [img.get("url") for img in images if img.get("url")]

        # Extract category/classification
        category = "Events"
        if "classifications" in tm_event:
            classifications = tm_event["classifications"]
            if classifications:
                classification = classifications[0]
                # Prefer segment > genre > subGenre
                if "segment" in classification:
                    category = classification["segment"].get("name", "Events")
                elif "genre" in classification:
                    category = classification["genre"].get("name", "Events")

        # Extract description
        description = tm_event.get("info") or tm_event.get("pleaseNote") or f"See {name} live! Get tickets now on Ticketmaster."

        # Build our event format
        return {
            "id": f"tm_{event_id}",
            "title": name,
            "organization": "Ticketmaster",
            "description": description,
            "date_start": date_start,
            "location_address": address,
            "city": city,
            "state": state,
            "zip": zip_code,
            "latitude": latitude,
            "longitude": longitude,
            "category": category,
            "url": url,
            "source": "Ticketmaster",
            "venue": venue_name,
            "price": price_str,
            "image_url": image_url,
            "image_urls": image_urls,
            # Note: Ticketmaster events don't have volunteer contact info
            "contact_email": None,
            "contact_phone": None,
            "contact_person": None,
        }

    def get_events_for_city(
        self,
        city: str,
        state_code: str,
        limit: int = 50,
        classification: str = None
    ) -> List[Dict]:
        """
        Get future events for a specific city in our app's format.

        Args:
            city: City name (e.g., "Dallas")
            state_code: State code (e.g., "TX")
            limit: Maximum number of events to return
            classification: Optional filter (Music, Sports, Arts & Theatre, etc.)

        Returns:
            List of events in our app's format
        """
        # Fetch from Ticketmaster
        tm_events = self.search_events(
            city=city,
            state_code=state_code,
            size=min(limit, 200),  # API max is 200
            classification_name=classification,
        )

        # Convert to our format
        events = []
        for tm_event in tm_events:
            try:
                event = self.convert_to_app_format(tm_event)
                events.append(event)
            except Exception as e:
                print(f"Error converting event {tm_event.get('id', 'unknown')}: {e}")
                continue

        return events[:limit]


# Example usage
if __name__ == "__main__":
    api = TicketmasterAPI()

    # Test search
    print("🎫 Testing Ticketmaster API...\n")

    cities = [
        ("Dallas", "TX"),
        ("Houston", "TX"),
        ("New York", "NY"),
        ("Los Angeles", "CA"),
    ]

    for city, state in cities:
        print(f"📍 {city}, {state}")
        events = api.get_events_for_city(city, state, limit=3)

        if events:
            print(f"   Found {len(events)} events:")
            for event in events:
                print(f"   ✅ {event['title']} - {event['venue']}")
                print(f"      {event['date_start']} | {event['price']}")
        else:
            print("   ❌ No events found")

        print()
