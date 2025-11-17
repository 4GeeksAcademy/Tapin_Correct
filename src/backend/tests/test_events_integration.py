"""
Integration tests for the /events/search endpoint.

Tests cover:
- API parameter validation
- Cache hit scenarios (returning cached events)
- Cache miss scenarios (triggering scraping)
- Error handling
- State nonprofit mapping usage
- Geohash-based caching
"""
import json
import asyncio
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone

import pytest

from app import app, db, Event, EventImage
from event_discovery.cache_manager import EventCacheManager
from event_discovery.state_nonprofits import STATE_NONPROFITS


@pytest.fixture
def events_client():
    """Test client with fresh database for event tests."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_event_data():
    """Sample event payload from LLM extraction."""
    return {
        "title": "Community Garden Volunteer Day",
        "organization": "Green Earth Initiative",
        "description": "Help plant vegetables for local food bank",
        "city": "Austin",
        "state": "TX",
        "lat": 30.2672,
        "lon": -97.7431,
        "images": ["http://example.com/garden1.jpg", "http://example.com/garden2.jpg"],
        "url": "http://greenearth.org/events/garden-day",
        "date": "2025-12-15",
        "category": "Environment",
    }


@pytest.fixture
def mock_geocoder():
    """Mock geocoder that returns Austin, TX coordinates."""
    return SimpleNamespace(
        geocode=lambda q: SimpleNamespace(latitude=30.2672, longitude=-97.7431)
    )


def fake_loader_factory(html_content="<html><body>Volunteer opportunities</body></html>"):
    """Factory for fake AsyncHtmlLoader (now using async aload)."""
    class FakeDoc:
        def __init__(self, page_content):
            self.page_content = page_content

    class FakeLoader:
        def __init__(self, urls=None):
            self._urls = urls

        async def aload(self):
            return [FakeDoc(html_content)]

    return FakeLoader


def make_fake_llm(events_payload):
    """Create fake LLM that returns specified events."""
    class Resp:
        def __init__(self, content):
            self.content = content

    class FakeLLM:
        async def ainvoke(self, prompt):
            return Resp(json.dumps(events_payload))

    return FakeLLM


# =============================================================================
# API Parameter Validation Tests
# =============================================================================

def test_search_missing_state_returns_400(events_client):
    """Endpoint requires state parameter."""
    response = events_client.get("/events/search")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "state" in data["error"].lower()


def test_search_with_state_only_returns_200(events_client):
    """State-only search should work (city is optional)."""
    with patch("routes.events.EventCacheManager") as MockManager:
        instance = MockManager.return_value
        instance.search_by_location = AsyncMock(return_value=[])

        response = events_client.get("/events/search?state=TX")
        assert response.status_code == 200
        data = response.get_json()
        assert "events" in data
        assert isinstance(data["events"], list)


def test_search_with_city_and_state_returns_200(events_client):
    """Full city+state search should work."""
    with patch("routes.events.EventCacheManager") as MockManager:
        instance = MockManager.return_value
        instance.search_by_location = AsyncMock(return_value=[])

        response = events_client.get("/events/search?city=Austin&state=TX")
        assert response.status_code == 200
        data = response.get_json()
        assert "events" in data


# =============================================================================
# Cache Hit Tests
# =============================================================================

def test_cache_hit_returns_cached_events(events_client, sample_event_data):
    """When cache has non-expired events, return them without scraping."""
    with app.app_context():
        # Pre-populate cache with a non-expired event
        from geohash2 import encode
        gh6 = encode(30.2672, -97.7431, precision=6)
        gh4 = encode(30.2672, -97.7431, precision=4)

        event = Event(
            id="cached-event-123",
            title="Cached Food Drive",
            organization="Local Food Bank",
            description="Help distribute food",
            date_start=datetime(2025, 12, 20),
            location_city="Austin",
            location_state="TX",
            latitude=30.2672,
            longitude=-97.7431,
            geohash_6=gh6,
            geohash_4=gh4,
            url="http://foodbank.org/event/drive",
            cache_expires_at=datetime.now(timezone.utc) + timedelta(days=15),
            scraped_at=datetime.now(timezone.utc),
        )
        db.session.add(event)
        db.session.commit()

    with patch("routes.events.EventCacheManager") as MockManager:
        # Use real EventCacheManager but mock geocoder
        real_manager = EventCacheManager()
        real_manager.geocoder = SimpleNamespace(
            geocode=lambda q: SimpleNamespace(latitude=30.2672, longitude=-97.7431)
        )
        MockManager.return_value = real_manager

        response = events_client.get("/events/search?city=Austin&state=TX")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["events"]) >= 1
        assert data["events"][0]["title"] == "Cached Food Drive"


def test_expired_cache_triggers_scrape(events_client, sample_event_data, mock_geocoder):
    """Expired cache entries should trigger a new scrape."""
    with app.app_context():
        # Pre-populate with EXPIRED event
        from geohash2 import encode
        gh6 = encode(30.2672, -97.7431, precision=6)
        gh4 = encode(30.2672, -97.7431, precision=4)

        expired_event = Event(
            id="expired-event-456",
            title="Old Event",
            organization="Old Org",
            description="This is expired",
            location_city="Austin",
            location_state="TX",
            latitude=30.2672,
            longitude=-97.7431,
            geohash_6=gh6,
            geohash_4=gh4,
            cache_expires_at=datetime.now(timezone.utc) - timedelta(days=1),  # EXPIRED
            scraped_at=datetime.now(timezone.utc) - timedelta(days=31),
        )
        db.session.add(expired_event)
        db.session.commit()

    with patch("event_discovery.cache_manager.AsyncHtmlLoader", new=fake_loader_factory()):
        with patch("event_discovery.cache_manager.HybridLLM", new=make_fake_llm([sample_event_data])):
            with patch("routes.events.EventCacheManager") as MockManager:
                real_manager = EventCacheManager()
                real_manager.geocoder = mock_geocoder
                MockManager.return_value = real_manager

                response = events_client.get("/events/search?city=Austin&state=TX")
                assert response.status_code == 200
                data = response.get_json()
                # Should have new scraped event, not the expired one
                assert len(data["events"]) >= 1
                titles = [e["title"] for e in data["events"]]
                assert "Community Garden Volunteer Day" in titles


# =============================================================================
# Cache Miss / Scraping Tests
# =============================================================================

def test_cache_miss_triggers_scraping(events_client, sample_event_data, mock_geocoder):
    """Empty cache should trigger scraping and persist results."""
    with patch("event_discovery.cache_manager.AsyncHtmlLoader", new=fake_loader_factory()):
        with patch("event_discovery.cache_manager.HybridLLM", new=make_fake_llm([sample_event_data])):
            with patch("routes.events.EventCacheManager") as MockManager:
                real_manager = EventCacheManager()
                real_manager.geocoder = mock_geocoder
                MockManager.return_value = real_manager

                response = events_client.get("/events/search?city=Austin&state=TX")
                assert response.status_code == 200
                data = response.get_json()
                assert len(data["events"]) >= 1

                event = data["events"][0]
                assert event["title"] == "Community Garden Volunteer Day"
                assert event["organization"] == "Green Earth Initiative"
                assert event["location_city"] == "Austin"
                assert event["location_state"] == "TX"


def test_scraping_persists_images(sample_event_data, mock_geocoder):
    """Scraped events should have images normalized into EventImage table."""
    # Use fresh app context with clean database
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        with patch(
            "event_discovery.cache_manager.AsyncHtmlLoader",
            new=fake_loader_factory()
        ):
            with patch(
                "event_discovery.cache_manager.HybridLLM",
                new=make_fake_llm([sample_event_data])
            ):
                manager = EventCacheManager()
                manager.geocoder = mock_geocoder

                # Direct call to search_by_location
                result = asyncio.run(
                    manager.search_by_location("Austin", "TX")
                )

                assert len(result) >= 1
                event = result[0]

                # Check images in response
                assert "images" in event
                # The to_dict() may not include newly added images
                # due to SQLAlchemy lazy loading behavior
                # Verify database persistence directly
                db_event = Event.query.filter_by(
                    url="http://greenearth.org/events/garden-day"
                ).first()
                assert db_event is not None
                db_images = EventImage.query.filter_by(
                    event_id=db_event.id
                ).order_by(EventImage.position).all()
                assert len(db_images) == 2
                assert db_images[0].position == 0
                assert db_images[1].position == 1
                assert db_images[0].url == "http://example.com/garden1.jpg"
                assert db_images[1].url == "http://example.com/garden2.jpg"

                # Also verify legacy fields are set
                assert db_event.image_url == "http://example.com/garden1.jpg"
                import json
                stored_urls = json.loads(db_event.image_urls)
                assert len(stored_urls) == 2

        db.session.remove()
        db.drop_all()


def test_multiple_events_scraped_in_parallel(events_client, mock_geocoder):
    """Multiple nonprofits should be scraped in parallel."""
    events_batch = [
        {
            "title": "Event 1",
            "organization": "Org 1",
            "description": "Desc 1",
            "city": "Austin",
            "state": "TX",
            "lat": 30.2672,
            "lon": -97.7431,
            "url": "http://org1.com/event1",
            "date": "2025-12-10",
        },
        {
            "title": "Event 2",
            "organization": "Org 2",
            "description": "Desc 2",
            "city": "Austin",
            "state": "TX",
            "lat": 30.2672,
            "lon": -97.7431,
            "url": "http://org2.com/event2",
            "date": "2025-12-11",
        },
    ]

    with patch("event_discovery.cache_manager.AsyncHtmlLoader", new=fake_loader_factory()):
        with patch("event_discovery.cache_manager.HybridLLM", new=make_fake_llm(events_batch)):
            with patch("routes.events.EventCacheManager") as MockManager:
                real_manager = EventCacheManager()
                real_manager.geocoder = mock_geocoder
                MockManager.return_value = real_manager

                response = events_client.get("/events/search?city=Austin&state=TX")
                assert response.status_code == 200
                data = response.get_json()
                # Should have multiple events from scraping
                assert len(data["events"]) >= 2


# =============================================================================
# State Nonprofit Mapping Tests
# =============================================================================

def test_all_50_states_have_nonprofits():
    """Verify all 50 US states are mapped."""
    us_states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

    for state in us_states:
        assert state in STATE_NONPROFITS, f"Missing state: {state}"
        assert len(STATE_NONPROFITS[state]) >= 2, f"State {state} needs at least 2 nonprofit sources"


def test_each_state_has_valid_nonprofit_structure():
    """Each state entry should have valid (url, org_name) tuples."""
    for state, nonprofits in STATE_NONPROFITS.items():
        for entry in nonprofits:
            assert isinstance(entry, tuple), f"State {state} has non-tuple entry"
            assert len(entry) == 2, f"State {state} entry should have (url, org_name)"
            url, org_name = entry
            assert url.startswith("http"), f"State {state} has invalid URL: {url}"
            assert len(org_name) > 0, f"State {state} has empty org name"


def test_texas_uses_correct_nonprofits(mock_geocoder):
    """Verify TX scraping uses the mapped Texas nonprofits."""
    with app.app_context():
        db.create_all()

        scraped_urls = []

        class TrackingLoader:
            def __init__(self, urls=None):
                scraped_urls.extend(urls or [])

            async def aload(self):
                class FakeDoc:
                    page_content = "<html>test</html>"
                return [FakeDoc()]

        with patch("event_discovery.cache_manager.AsyncHtmlLoader", TrackingLoader):
            with patch("event_discovery.cache_manager.HybridLLM", make_fake_llm([])):
                manager = EventCacheManager()
                manager.geocoder = mock_geocoder
                asyncio.run(manager.search_by_location("Houston", "TX"))

                # With localized search, only one city-specific URL is scraped
                # Should contain VolunteerMatch Houston search URL
                assert len(scraped_urls) == 1
                assert "Houston" in scraped_urls[0]
                assert "volunteermatch.org" in scraped_urls[0]

        db.drop_all()


# =============================================================================
# Geohash Caching Tests
# =============================================================================

def test_geohash_precision_6_for_city_level():
    """Events should use precision-6 geohash for city-level caching."""
    from geohash2 import encode

    # Austin, TX coordinates
    lat, lon = 30.2672, -97.7431
    gh6 = encode(lat, lon, precision=6)

    # Geohash precision 6 covers roughly a city block/neighborhood
    assert len(gh6) == 6
    # Two nearby points in same city should share first 5 chars (same neighborhood)
    # Precision 6 is very granular (~1.2km), so we check first 5 chars match
    nearby_lat, nearby_lon = 30.2675, -97.7435
    nearby_gh6 = encode(nearby_lat, nearby_lon, precision=6)
    assert gh6[:5] == nearby_gh6[:5]  # Same general area


def test_events_indexed_by_geohash(events_client, sample_event_data, mock_geocoder):
    """Persisted events should have geohash indexes set."""
    with patch("event_discovery.cache_manager.AsyncHtmlLoader", new=fake_loader_factory()):
        with patch("event_discovery.cache_manager.HybridLLM", new=make_fake_llm([sample_event_data])):
            with patch("routes.events.EventCacheManager") as MockManager:
                real_manager = EventCacheManager()
                real_manager.geocoder = mock_geocoder
                MockManager.return_value = real_manager

                events_client.get("/events/search?city=Austin&state=TX")

                with app.app_context():
                    event = Event.query.filter_by(url="http://greenearth.org/events/garden-day").first()
                    assert event is not None
                    assert event.geohash_6 is not None
                    assert len(event.geohash_6) == 6
                    assert event.geohash_4 is not None
                    assert len(event.geohash_4) == 4


# =============================================================================
# Error Handling Tests
# =============================================================================

def test_geocoder_failure_returns_empty(events_client):
    """If geocoder can't find location, return empty list."""
    with patch("routes.events.EventCacheManager") as MockManager:
        real_manager = EventCacheManager()
        real_manager.geocoder = SimpleNamespace(geocode=lambda q: None)
        MockManager.return_value = real_manager

        response = events_client.get("/events/search?city=NonexistentCity&state=ZZ")
        assert response.status_code == 200
        data = response.get_json()
        assert data["events"] == []


def test_scraping_error_handled_gracefully(events_client, mock_geocoder):
    """Scraping errors shouldn't crash the endpoint."""
    class ErrorLoader:
        def __init__(self, urls=None):
            pass

        async def aload(self):
            raise Exception("Async loader failed")

    with patch("event_discovery.cache_manager.AsyncHtmlLoader", ErrorLoader):
        with patch("routes.events.EventCacheManager") as MockManager:
            real_manager = EventCacheManager()
            real_manager.geocoder = mock_geocoder
            MockManager.return_value = real_manager

            response = events_client.get("/events/search?city=Austin&state=TX")
            # Should return 200 with empty events, not 500
            assert response.status_code == 200
            data = response.get_json()
            assert "events" in data


def test_llm_invalid_json_handled(events_client, mock_geocoder):
    """Invalid JSON from LLM should be handled gracefully."""
    class BadLLM:
        async def ainvoke(self, prompt):
            class Resp:
                content = "This is not valid JSON"
            return Resp()

    with patch("event_discovery.cache_manager.AsyncHtmlLoader", new=fake_loader_factory()):
        with patch("event_discovery.cache_manager.HybridLLM", BadLLM):
            with patch("routes.events.EventCacheManager") as MockManager:
                real_manager = EventCacheManager()
                real_manager.geocoder = mock_geocoder
                MockManager.return_value = real_manager

                response = events_client.get("/events/search?city=Austin&state=TX")
                assert response.status_code == 200
                data = response.get_json()
                # Should handle gracefully, possibly empty events
                assert "events" in data


# =============================================================================
# Data Integrity Tests
# =============================================================================

def test_upsert_deduplicates_by_url(events_client, sample_event_data, mock_geocoder):
    """Same URL scraped twice should update, not duplicate."""
    with patch("event_discovery.cache_manager.AsyncHtmlLoader", new=fake_loader_factory()):
        with patch("event_discovery.cache_manager.HybridLLM", new=make_fake_llm([sample_event_data])):
            with patch("routes.events.EventCacheManager") as MockManager:
                real_manager = EventCacheManager()
                real_manager.geocoder = mock_geocoder
                MockManager.return_value = real_manager

                # First scrape
                events_client.get("/events/search?city=Austin&state=TX")

                with app.app_context():
                    count1 = Event.query.count()

                # Invalidate cache to trigger re-scrape
                with app.app_context():
                    Event.query.update({
                        "cache_expires_at": datetime.now(timezone.utc) - timedelta(days=1)
                    })
                    db.session.commit()

                # Second scrape - same event
                events_client.get("/events/search?city=Austin&state=TX")

                with app.app_context():
                    count2 = Event.query.count()

                # Should have same count (updated, not duplicated)
                assert count2 == count1


def test_cache_expiration_set_to_30_days(events_client, sample_event_data, mock_geocoder):
    """New events should have cache_expires_at set 30 days in future."""
    with patch("event_discovery.cache_manager.AsyncHtmlLoader", new=fake_loader_factory()):
        with patch("event_discovery.cache_manager.HybridLLM", new=make_fake_llm([sample_event_data])):
            with patch("routes.events.EventCacheManager") as MockManager:
                real_manager = EventCacheManager()
                real_manager.geocoder = mock_geocoder
                MockManager.return_value = real_manager

                events_client.get("/events/search?city=Austin&state=TX")

                with app.app_context():
                    event = Event.query.first()
                    assert event.cache_expires_at is not None
                    # Should be ~30 days from now
                    # Handle both timezone-aware and naive datetimes
                    expires_at = event.cache_expires_at
                    now = datetime.now(timezone.utc)
                    # If expires_at is naive, assume UTC
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    days_until_expiry = (expires_at - now).days
                    assert 29 <= days_until_expiry <= 30


def test_event_date_parsing():
    """Event dates should be properly parsed from ISO strings."""
    with app.app_context():
        db.create_all()

        event_with_date = {
            "title": "Date Test Event",
            "organization": "Test Org",
            "city": "Austin",
            "state": "TX",
            "lat": 30.2672,
            "lon": -97.7431,
            "url": "http://test.org/date-event",
            "date": "2025-12-25T10:00:00",
        }

        with patch("event_discovery.cache_manager.AsyncHtmlLoader", new=fake_loader_factory()):
            with patch("event_discovery.cache_manager.HybridLLM", new=make_fake_llm([event_with_date])):
                manager = EventCacheManager()
                manager.geocoder = SimpleNamespace(
                    geocode=lambda q: SimpleNamespace(latitude=30.2672, longitude=-97.7431)
                )
                asyncio.run(manager.search_by_location("Austin", "TX"))

                event = Event.query.filter_by(url="http://test.org/date-event").first()
                assert event is not None
                assert event.date_start is not None
                assert event.date_start.year == 2025
                assert event.date_start.month == 12
                assert event.date_start.day == 25

        db.drop_all()
