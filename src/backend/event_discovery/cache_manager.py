import asyncio
import json
import uuid
import logging
import pygeohash as geohash
from geopy.geocoders import Nominatim
import sqlalchemy as sa
from langchain_community.document_loaders import AsyncHtmlLoader
from bs4 import BeautifulSoup
from .llm_impl import HybridLLM
from datetime import datetime, timedelta, timezone
from .state_nonprofits import STATE_NONPROFITS
from .facebook_scraper import FacebookEventScraper
from .local_events_scraper import LocalEventsScraper

logger = logging.getLogger(__name__)

# Try to import playwright for JavaScript rendering
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Import DB models from the application package
# Use late binding to avoid circular import issues with Flask app context
def _get_db():
    from backend.app import db
    return db


def _get_models():
    from backend.app import Event, EventImage
    return Event, EventImage


class EventCacheManager:

    def __init__(self, db=None, event_model=None, event_image_model=None):
        # HybridLLM prefers Gemini; falls back to Ollama or a mock.
        self.llm = HybridLLM()
        self.geocoder = Nominatim(user_agent="tapin_app", timeout=10)
        self.facebook_scraper = FacebookEventScraper()
        self.local_scraper = LocalEventsScraper()
        # Store db and models if provided, otherwise get them later
        self.db = db
        self.Event = event_model
        self.EventImage = event_image_model

    async def search_by_location(self, city: str, state: str):
        # Use provided models or get them from app context
        if self.db is None or self.Event is None:
            db = _get_db()
            Event, EventImage = _get_models()
        else:
            db = self.db
            Event = self.Event
            EventImage = self.EventImage

        location = self.geocoder.geocode(f"{city}, {state}, USA")
        if not location:
            return []

        lat, lon = location.latitude, location.longitude

        # Cache lookup by geohash_6 (city-level) and ensure not expired
        gh = geohash.encode(lat, lon, precision=6)
        now = datetime.now(timezone.utc)
        cached_q = Event.query.filter(Event.geohash_6 == gh).filter(
            sa.or_(
                Event.cache_expires_at.is_(None),
                Event.cache_expires_at > now,
            )
        )
        cached = cached_q.all()
        if cached:
            return [e.to_dict() for e in cached]

        # Cache miss -> scrape ONLY for this specific city (localized search)
        events = await self.scrape_city_events(city, state)
        # Deduplicate events by URL before processing
        seen_urls = set()
        unique_events = []
        for event in events:
            url = event.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_events.append(event)
            elif not url:
                # Keep events without URLs (can't dedupe)
                unique_events.append(event)
        persisted = []
        for event in unique_events:
            # Normalize lat/lon: prefer event-provided, else use search center
            ev_lat = event.get("lat") or lat
            ev_lon = event.get("lon") or lon
            gh6 = geohash.encode(float(ev_lat), float(ev_lon), precision=6)
            gh4 = geohash.encode(float(ev_lat), float(ev_lon), precision=4)
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)

            # Upsert into DB: prefer matching by URL when available
            try:
                existing = None
                url = event.get("url")
                if url:
                    existing = Event.query.filter_by(url=url).first()
                # Normalize date field: prefer datetime, parse iso strings
                date_raw = event.get("date")
                date_obj = None
                if date_raw:
                    if isinstance(date_raw, str):
                        try:
                            date_obj = datetime.fromisoformat(date_raw)
                        except Exception:
                            # best-effort: leave as None if parse fails
                            date_obj = None
                    elif isinstance(date_raw, datetime):
                        date_obj = date_raw

                if not existing:
                    # Fallback: match by title + org + date
                    existing = Event.query.filter_by(
                        title=event.get("title"),
                        organization=event.get("organization"),
                        date_start=date_obj,
                    ).first()

                if existing:
                    # update fields
                    existing.description = event.get("description")
                    existing.latitude = float(ev_lat)
                    existing.longitude = float(ev_lon)
                    # update date if we parsed one
                    if date_obj:
                        existing.date_start = date_obj
                    existing.geohash_6 = gh6
                    existing.geohash_4 = gh4
                    existing.cache_expires_at = expires_at
                    existing.scraped_at = datetime.now(timezone.utc)
                    # update image fields and normalized images
                    imgs = event.get("images") or []
                    # Support image_urls as JSON/text
                    if not imgs and event.get("image_urls"):
                        try:
                            imgs = json.loads(event.get("image_urls"))
                        except Exception:
                            raw = str(event.get("image_urls"))
                            parts = [p.strip() for p in raw.split(",")]
                            imgs = [p for p in parts if p]

                    # Also support single image_url field
                    if not imgs and event.get("image_url"):
                        imgs = [event.get("image_url")]

                    # Update legacy fields
                    # Update legacy thumbnail/url fields
                    if imgs:
                        existing.image_url = event.get("image_url") or imgs[0]
                        existing.image_urls = json.dumps(imgs)
                    else:
                        existing.image_url = (
                            event.get("image_url") or existing.image_url
                        )
                        existing.image_urls = existing.image_urls

                    # Clear existing normalized images and repopulate
                    if imgs:
                        # remove old images for this event using ORM
                        # to keep session in sync
                        for old_img in list(existing.images):
                            db.session.delete(old_img)
                        # Flush deletes before adding new images
                        db.session.flush()
                        for idx, img_data in enumerate(imgs):
                            # Handle both string URLs and dict with url/caption
                            if isinstance(img_data, dict):
                                img_url = img_data.get('url')
                                img_caption = img_data.get('caption')
                            else:
                                img_url = img_data
                                img_caption = None

                            ei = EventImage(
                                event_id=existing.id,
                                url=img_url,
                                caption=img_caption,
                                position=idx,
                            )
                            db.session.add(ei)

                    db.session.add(existing)
                    persisted.append(existing.to_dict())
                else:
                    ev = Event(
                        id=str(uuid.uuid4()),
                        title=event.get("title") or "",
                        organization=event.get("organization") or "",
                        description=event.get("description"),
                        date_start=date_obj or None,
                        location_address=event.get("location_address"),
                        location_city=event.get("city") or city,
                        location_state=event.get("state") or state,
                        location_zip=event.get("zip"),
                        latitude=(float(ev_lat) if ev_lat is not None else None),
                        longitude=(float(ev_lon) if ev_lon is not None else None),
                        geohash_4=gh4,
                        geohash_6=gh6,
                        category=event.get("category"),
                        url=event.get("url"),
                        source=event.get("source"),
                        scraped_at=datetime.now(timezone.utc),
                        cache_expires_at=expires_at,
                    )
                    # Attach images if present
                    imgs = event.get("images") or []
                    if not imgs and event.get("image_urls"):
                        try:
                            imgs = json.loads(event.get("image_urls"))
                        except Exception:
                            raw = str(event.get("image_urls"))
                            parts = [p.strip() for p in raw.split(",")]
                            imgs = [p for p in parts if p]
                    if not imgs and event.get("image_url"):
                        imgs = [event.get("image_url")]

                    # Handle first image - could be string or dict
                    first_img = None
                    if imgs:
                        if isinstance(imgs[0], dict):
                            first_img = imgs[0].get('url')
                        else:
                            first_img = imgs[0]
                    ev.image_url = event.get("image_url") or first_img
                    ev.image_urls = json.dumps(imgs) if imgs else None

                    db.session.add(ev)
                    # Add normalized EventImage rows
                    for idx, img_data in enumerate(imgs):
                        # Handle both string URLs and dict with url/caption
                        if isinstance(img_data, dict):
                            img_url = img_data.get('url')
                            img_caption = img_data.get('caption')
                        else:
                            img_url = img_data
                            img_caption = None

                        ei = EventImage(
                            event_id=ev.id,
                            url=img_url,
                            caption=img_caption,
                            position=idx,
                        )
                        db.session.add(ei)
                    persisted.append(ev.to_dict())
            except Exception as e:
                logger.error(f"DB upsert error for event {event.get('title')}: {e}")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"DB commit error: {e}")

        # Return persisted records (or empty list)
        return persisted

    async def scrape_city_events(self, city: str, state: str):
        """Scrape events ONLY for the user's specific city location.

        Combines multiple sources:
        1. Facebook nonprofit pages (with images)
        2. VolunteerMatch search
        3. Sample events fallback

        Falls back gracefully if scraping fails.
        """
        state_upper = state.upper() if state else ""
        all_events = []

        # Try Facebook nonprofit pages first (includes images)
        try:
            fb_events = await self.facebook_scraper.search_events(
                city, state_upper, limit=3
            )
            # Process Facebook events to extract images
            for event in fb_events:
                # Convert Facebook image format to our format
                if 'images' in event and event['images']:
                    event['image_urls'] = [
                        img['url'] for img in event['images']
                    ]
                    event['image_url'] = event['images'][0]['url']
                all_events.extend(fb_events)
        except Exception as e:
            logger.warning(f"Facebook scraping failed: {e}")

        # Try VolunteerMatch
        city_slug = city.replace(" ", "%20") if city else ""
        volunteer_match_url = (
            f"https://www.volunteermatch.org/search?"
            f"l={city_slug}%2C+{state_upper}"
        )
        org_name = f"VolunteerMatch {city}, {state_upper}"

        vm_events = await self.scrape_nonprofit(volunteer_match_url, org_name)
        all_events.extend(vm_events)

        # If no events found, generate samples with images
        if not all_events:
            logger.info(
                f"No events found for {city}, {state_upper}. "
                "Generating sample events."
            )
            all_events = self._generate_sample_events_with_images(
                city, state_upper
            )

        # Ensure all events have city/state
        for event in all_events:
            if not event.get("city"):
                event["city"] = city
            if not event.get("state"):
                event["state"] = state_upper

        return all_events

    def _generate_sample_events_with_images(self, city: str, state: str):
        """Generate localized sample volunteer events WITH IMAGES.

        These represent common volunteer opportunities with realistic images.
        Each event has a unique URL to avoid deduplication.
        """
        base_url = f"https://volunteermatch.org/search?l={city}%2C+{state}"

        # Placeholder images for different categories
        images = {
            "food": [
                "https://via.placeholder.com/800x600/4CAF50/ffffff"
                "?text=Food+Bank+Volunteers",
                "https://via.placeholder.com/800x600/4CAF50/ffffff"
                "?text=Food+Distribution"
            ],
            "animals": [
                "https://via.placeholder.com/800x600/FF9800/ffffff"
                "?text=Shelter+Dogs",
                "https://via.placeholder.com/800x600/FF9800/ffffff"
                "?text=Dog+Walking"
            ],
            "environment": [
                "https://via.placeholder.com/800x600/2196F3/ffffff"
                "?text=Park+Cleanup",
                "https://via.placeholder.com/800x600/2196F3/ffffff"
                "?text=Tree+Planting"
            ],
            "education": [
                "https://via.placeholder.com/800x600/9C27B0/ffffff"
                "?text=Tutoring+Session",
                "https://via.placeholder.com/800x600/9C27B0/ffffff"
                "?text=Library+Program"
            ],
            "seniors": [
                "https://via.placeholder.com/800x600/F44336/ffffff"
                "?text=Senior+Center",
                "https://via.placeholder.com/800x600/F44336/ffffff"
                "?text=Companion+Program"
            ],
        }

        return [
            {
                "title": f"Community Food Bank Sorting",
                "organization": f"{city} Food Bank",
                "description": f"Help sort and package donated food items for distribution to families in need in {city}.",
                "city": city,
                "state": state,
                "lat": 0.0,
                "lon": 0.0,
                "url": f"{base_url}#foodbank",
                "date": "2025-01-25",
                "category": "Hunger Relief",
                "image_url": images["food"][0],
                "image_urls": images["food"],
            },
            {
                "title": f"Animal Shelter Dog Walking",
                "organization": f"{city} Humane Society",
                "description": f"Walk and socialize shelter dogs to help them get adopted. All experience levels welcome.",
                "city": city,
                "state": state,
                "lat": 0.0,
                "lon": 0.0,
                "url": f"{base_url}#animals",
                "date": "2025-01-26",
                "category": "Animals",
                "image_url": images["animals"][0],
                "image_urls": images["animals"],
            },
            {
                "title": f"Park Cleanup & Beautification",
                "organization": f"{city} Parks Department",
                "description": f"Join fellow volunteers to clean up litter and plant native flowers in local parks.",
                "city": city,
                "state": state,
                "lat": 0.0,
                "lon": 0.0,
                "url": f"{base_url}#environment",
                "date": "2025-02-01",
                "category": "Environment",
                "image_url": images["environment"][0],
                "image_urls": images["environment"],
            },
            {
                "title": f"Youth Tutoring Program",
                "organization": f"{city} Public Library",
                "description": f"Tutor K-12 students in math, reading, or science. Make a difference in a young person's education.",
                "city": city,
                "state": state,
                "lat": 0.0,
                "lon": 0.0,
                "url": f"{base_url}#education",
                "date": "2025-02-08",
                "category": "Education",
                "image_url": images["education"][0],
                "image_urls": images["education"],
            },
            {
                "title": f"Senior Center Companion",
                "organization": f"{city} Senior Services",
                "description": f"Visit with seniors, play games, or help with activities. Combat loneliness and make meaningful connections.",
                "city": city,
                "state": state,
                "lat": 0.0,
                "lon": 0.0,
                "url": f"{base_url}#seniors",
                "date": "2025-02-15",
                "category": "Seniors",
                "image_url": images["seniors"][0],
                "image_urls": images["seniors"],
            },
        ]

    # Keep old method name for compatibility
    def _generate_sample_events(self, city: str, state: str):
        """Backwards compatibility - calls new method with images."""
        return self._generate_sample_events_with_images(city, state)

    async def scrape_state_nonprofits(self, state: str):
        # Use the curated STATE_NONPROFITS mapping; fall back to a minimal list
        key = state.upper() if state else ""
        nonprofits = STATE_NONPROFITS.get(
            key,
            [
                ("https://volunteerhouston.org/needs", "Volunteer Houston"),
                ("https://houstonarboretum.org/volunteer", "Houston Arboretum"),
            ],
        )
        tasks = []
        for url, org in nonprofits[:10]:
            tasks.append(self.scrape_nonprofit(url, org))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_events = []
        for r in results:
            if isinstance(r, list):
                all_events.extend(r)
        return all_events

    async def _fetch_page_content(self, url: str) -> str:
        """Fetch page content, using Playwright for JS rendering if available."""
        import os

        # Skip Playwright in test environment to allow mocking
        use_playwright = PLAYWRIGHT_AVAILABLE and "PYTEST_CURRENT_TEST" not in os.environ

        if use_playwright:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    # Wait for content to load
                    await page.wait_for_timeout(2000)
                    content = await page.content()
                    await browser.close()
                    return content
            except Exception as e:
                logger.info(f"Playwright fetch failed: {e}, falling back to basic HTTP")

        # Fallback to basic HTTP fetch
        loader = AsyncHtmlLoader([url])
        docs = await loader.aload()
        if docs:
            return docs[0].page_content
        return ""

    async def scrape_nonprofit(self, url: str, org_name: str):
        try:
            # Fetch page content (with JS rendering if Playwright available)
            raw_html = await self._fetch_page_content(url)
            if not raw_html:
                logger.info(f"No content loaded from {url}")
                return []
            # Extract text content from HTML using BeautifulSoup
            soup = BeautifulSoup(raw_html, "html.parser")
            # Remove script and style elements
            for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                tag.decompose()
            # Get text content
            text = soup.get_text(separator="\n", strip=True)
            # Clean up excessive whitespace
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            clean_text = "\n".join(lines)
            # Build a structured prompt optimized for Ollama/local models
            page_snippet = clean_text[:6000]  # More context with clean text
            prompt = f"""You are a JSON extraction assistant. Extract volunteer opportunities from the webpage below.

TASK: Find volunteer events/opportunities and return them as a JSON array.

REQUIRED OUTPUT FORMAT (return ONLY this JSON, no other text):
[
  {{
    "title": "Event Name",
    "description": "Brief description of the volunteer opportunity",
    "organization": "{org_name}",
    "city": "City Name",
    "state": "State Code (e.g. TX)",
    "lat": 0.0,
    "lon": 0.0,
    "url": "https://link-to-event",
    "date": "2025-01-01"
  }}
]

If no volunteer opportunities are found, return: []

WEBPAGE CONTENT FROM {org_name}:
{page_snippet}

JSON OUTPUT:"""
            result = await self.llm.ainvoke(prompt)
            # Parse JSON from response, handle potential markdown wrapping
            content = result.content.strip()
            # Remove markdown code fence if present
            if content.startswith("```"):
                lines = content.split("\n")
                # Find the closing fence
                if len(lines) > 2 and lines[-1].strip().startswith("```"):
                    content = "\n".join(lines[1:-1])
                else:
                    content = "\n".join(lines[1:])
            # Try to find JSON array in response
            if "[" in content:
                start = content.index("[")
                # Find matching closing bracket
                depth = 0
                end = start
                for i in range(start, len(content)):
                    if content[i] == "[":
                        depth += 1
                    elif content[i] == "]":
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                content = content[start:end]
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.info(f"JSON parse error for {org_name}: {e}")
            logger.info(f"Raw response: {result.content[:500]}...")
            return []
        except Exception as e:
            logger.info(f"Error scraping {org_name}: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def discover_tonight(self, city: str, state: str, limit: int = 20):
        """
        Discover ALL types of local events happening tonight (not just volunteer).

        Uses LocalEventsScraper to find events across multiple platforms:
        - Eventbrite
        - Meetup
        - Facebook local events
        - City event calendars

        Args:
            city: City name
            state: State code
            limit: Maximum events to return

        Returns:
            List of event dictionaries with images
        """
        # Use provided models or get them from app context
        if self.db is None or self.Event is None:
            db = _get_db()
            Event, EventImage = _get_models()
        else:
            db = self.db
            Event = self.Event
            EventImage = self.EventImage

        # Geocode location
        location = self.geocoder.geocode(f"{city}, {state}, USA")
        if not location:
            return []

        lat, lon = location.latitude, location.longitude

        # Check cache first
        gh = geohash.encode(lat, lon, precision=6)
        now = datetime.now(timezone.utc)

        # For tonight's events, cache for shorter period (4 hours)
        cache_key = f"tonight_{gh}"
        cached_q = Event.query.filter(
            Event.geohash_6 == gh,
            Event.category.notin_(['Hunger Relief', 'Animals', 'Environment',
                                    'Education', 'Seniors'])  # Exclude volunteer categories
        ).filter(
            sa.or_(
                Event.cache_expires_at.is_(None),
                Event.cache_expires_at > now,
            )
        )
        cached = cached_q.limit(limit).all()

        if cached and len(cached) >= limit / 2:  # If we have at least half the requested events
            return [e.to_dict() for e in cached][:limit]

        # Cache miss -> discover tonight's events
        events = await self.local_scraper.discover_tonight(city, state, limit)

        # Persist to database
        persisted = []
        for event in events:
            try:
                ev_lat = event.get("latitude") or lat
                ev_lon = event.get("longitude") or lon
                gh6 = geohash.encode(float(ev_lat), float(ev_lon), precision=6)
                gh4 = geohash.encode(float(ev_lat), float(ev_lon), precision=4)

                # Shorter cache for tonight's events (4 hours)
                expires_at = datetime.now(timezone.utc) + timedelta(hours=4)

                # Check if event already exists
                existing = None
                url = event.get("url")
                if url:
                    existing = Event.query.filter_by(url=url).first()

                if existing:
                    # Update existing event
                    existing.title = event.get("title")
                    existing.description = event.get("description")
                    existing.latitude = float(ev_lat)
                    existing.longitude = float(ev_lon)
                    existing.geohash_6 = gh6
                    existing.geohash_4 = gh4
                    existing.cache_expires_at = expires_at
                    existing.scraped_at = datetime.now(timezone.utc)
                    existing.category = event.get("category")
                    existing.venue = event.get("venue")
                    existing.price = event.get("price")

                    # Update images
                    imgs = event.get("image_urls") or []
                    if isinstance(imgs, str):
                        try:
                            imgs = json.loads(imgs)
                        except:
                            imgs = []
                    existing.image_url = event.get("image_url") or (imgs[0] if imgs else None)
                    existing.image_urls = json.dumps(imgs) if imgs else None

                    persisted.append(existing.to_dict())
                else:
                    # Create new event
                    # Parse start_time if available
                    start_time = event.get("start_time")
                    if start_time and isinstance(start_time, str):
                        try:
                            start_time = datetime.fromisoformat(start_time)
                        except:
                            start_time = None

                    ev = Event(
                        id=str(uuid.uuid4()),
                        title=event.get("title", "Untitled Event"),
                        organization=event.get("source", "Local Event"),
                        description=event.get("description", ""),
                        location_city=city,
                        location_state=state.upper(),
                        location_address=event.get("address"),
                        latitude=float(ev_lat),
                        longitude=float(ev_lon),
                        geohash_6=gh6,
                        geohash_4=gh4,
                        category=event.get("category", "Community"),
                        date_start=start_time,
                        url=url or f"https://tapin.org/events/{city.lower()}-{uuid.uuid4()}",
                        venue=event.get("venue"),
                        price=event.get("price"),
                        scraped_at=datetime.now(timezone.utc),
                        cache_expires_at=expires_at,
                    )

                    # Add images
                    imgs = event.get("image_urls") or []
                    if isinstance(imgs, str):
                        try:
                            imgs = json.loads(imgs)
                        except:
                            imgs = []

                    # Handle first image - could be string or dict
                    first_img = None
                    if imgs:
                        if isinstance(imgs[0], dict):
                            first_img = imgs[0].get('url')
                        else:
                            first_img = imgs[0]
                    ev.image_url = event.get("image_url") or first_img
                    ev.image_urls = json.dumps(imgs) if imgs else None

                    db.session.add(ev)

                    # Add normalized EventImage rows
                    for idx, img_url in enumerate(imgs):
                        ei = EventImage(
                            event_id=ev.id,
                            url=img_url,
                            caption=None,
                            position=idx,
                        )
                        db.session.add(ei)

                    persisted.append(ev.to_dict())
            except Exception as e:
                logger.info(f"Error persisting tonight event {event.get('title')}: {e}")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"DB commit error for tonight's events: {e}")

        return persisted[:limit]
