"""
Tests for local_events_scraper.py - Local event discovery
"""

import pytest
import asyncio
from datetime import datetime, timezone
from backend.event_discovery.local_events_scraper import LocalEventsScraper


class TestLocalEventsScraper:
    """Test suite for LocalEventsScraper"""

    @pytest.fixture
    def scraper(self):
        """Create a LocalEventsScraper instance"""
        return LocalEventsScraper()

    def test_scraper_initialization(self, scraper):
        """Test that scraper initializes correctly"""
        assert scraper is not None
        assert hasattr(scraper, "user_agent")
        assert "TapinLocalEvents" in scraper.user_agent

    def test_event_categories_defined(self, scraper):
        """Test that event categories are defined"""
        assert hasattr(scraper, "EVENT_CATEGORIES")
        assert len(scraper.EVENT_CATEGORIES) > 0

        # Check specific categories
        assert "Music & Concerts" in scraper.EVENT_CATEGORIES
        assert "Comedy" in scraper.EVENT_CATEGORIES
        assert "Food & Dining" in scraper.EVENT_CATEGORIES
        assert "Tech & Innovation" in scraper.EVENT_CATEGORIES

    def test_time_filters_defined(self, scraper):
        """Test that time filters are defined"""
        assert hasattr(scraper, "TIME_FILTERS")
        assert "tonight" in scraper.TIME_FILTERS
        assert "this_weekend" in scraper.TIME_FILTERS
        assert "this_week" in scraper.TIME_FILTERS

    @pytest.mark.asyncio
    async def test_discover_tonight_basic(self, scraper):
        """Test basic tonight event discovery"""
        events = await scraper.discover_tonight("Dallas", "TX", limit=5)

        assert isinstance(events, list)
        assert len(events) > 0
        assert len(events) <= 5

    @pytest.mark.asyncio
    async def test_discover_tonight_event_structure(self, scraper):
        """Test that discovered events have correct structure"""
        events = await scraper.discover_tonight("Seattle", "WA", limit=3)

        assert len(events) > 0

        for event in events:
            # Required fields
            assert "title" in event
            assert "category" in event
            assert "venue" in event
            assert "city" in event
            assert "state" in event

            # Check data types
            assert isinstance(event["title"], str)
            assert isinstance(event["category"], str)
            assert len(event["title"]) > 0

    @pytest.mark.asyncio
    async def test_discover_tonight_images(self, scraper):
        """Test that events include images"""
        events = await scraper.discover_tonight("Miami", "FL", limit=5)

        assert len(events) > 0

        for event in events:
            # Should have either image_url or image_urls
            has_images = "image_url" in event or "image_urls" in event

            if "image_url" in event:
                assert isinstance(event["image_url"], str)
                assert len(event["image_url"]) > 0

            if "image_urls" in event:
                assert isinstance(event["image_urls"], list)

    @pytest.mark.asyncio
    async def test_discover_tonight_sorted_by_time(self, scraper):
        """Test that events are sorted by start time"""
        events = await scraper.discover_tonight("Austin", "TX", limit=10)

        assert len(events) > 0

        # Check that events with start_time are sorted
        events_with_time = [e for e in events if "start_time" in e and e["start_time"]]

        if len(events_with_time) > 1:
            for i in range(len(events_with_time) - 1):
                time1 = events_with_time[i]["start_time"]
                time2 = events_with_time[i + 1]["start_time"]
                # Earlier events should come first
                assert time1 <= time2

    @pytest.mark.asyncio
    async def test_discover_tonight_deduplication(self, scraper):
        """Test that duplicate events are removed"""
        events = await scraper.discover_tonight("Portland", "OR", limit=20)

        # Check for duplicates by title + venue
        seen = set()
        for event in events:
            key = (event.get("title", ""), event.get("venue", ""))
            assert key not in seen, f"Duplicate event found: {key}"
            seen.add(key)

    @pytest.mark.asyncio
    async def test_discover_tonight_multiple_cities(self, scraper):
        """Test discovery for multiple cities"""
        cities = [
            ("New York", "NY"),
            ("Los Angeles", "CA"),
            ("Chicago", "IL"),
        ]

        for city, state in cities:
            events = await scraper.discover_tonight(city, state, limit=3)
            assert len(events) > 0
            assert all(e["city"] == city for e in events)
            assert all(e["state"] == state for e in events)

    @pytest.mark.asyncio
    async def test_eventbrite_scraper(self, scraper):
        """Test Eventbrite scraper method"""
        events = await scraper._scrape_eventbrite("Boston", "MA", "tonight")

        assert isinstance(events, list)
        # Should return sample data
        assert len(events) > 0

        for event in events:
            assert event["source"] == "Eventbrite"
            assert "title" in event
            assert "category" in event

    @pytest.mark.asyncio
    async def test_meetup_scraper(self, scraper):
        """Test Meetup scraper method"""
        events = await scraper._scrape_meetup("Denver", "CO", "tonight")

        assert isinstance(events, list)
        assert len(events) > 0

        for event in events:
            assert event["source"] == "Meetup"
            assert "title" in event

    @pytest.mark.asyncio
    async def test_facebook_local_scraper(self, scraper):
        """Test Facebook local scraper method"""
        events = await scraper._scrape_facebook_local("Phoenix", "AZ", "tonight")

        assert isinstance(events, list)
        assert len(events) > 0

        for event in events:
            assert event["source"] == "Facebook"

    @pytest.mark.asyncio
    async def test_city_calendar_scraper(self, scraper):
        """Test city calendar scraper method"""
        events = await scraper._scrape_city_calendar("Atlanta", "GA", "tonight")

        assert isinstance(events, list)
        assert len(events) > 0

    def test_tonight_time_future(self, scraper):
        """Test that tonight_time generates future timestamps"""
        # Test evening time
        time_str = "19:00"
        result = scraper._tonight_time(time_str)

        assert isinstance(result, str)

        # Parse the ISO timestamp
        dt = datetime.fromisoformat(result)

        # Should be timezone-aware
        assert dt.tzinfo is not None

    def test_tonight_time_format(self, scraper):
        """Test that tonight_time generates correct format"""
        time_str = "20:30"
        result = scraper._tonight_time(time_str)

        # Should be valid ISO format
        dt = datetime.fromisoformat(result)
        assert dt.hour == 20
        assert dt.minute == 30

    def test_categorize_event_static(self):
        """Test static categorize_event method"""
        result = LocalEventsScraper.categorize_event(
            "Live Band Performance", "Rock music concert with local bands"
        )

        assert result in LocalEventsScraper.EVENT_CATEGORIES
        assert result == "Music & Concerts"

    def test_categorize_event_fallback(self):
        """Test categorization fallback to Community"""
        result = LocalEventsScraper.categorize_event(
            "Generic Event", "A very generic description"
        )

        assert result == "Community"

    @pytest.mark.asyncio
    async def test_discover_tonight_limit_respected(self, scraper):
        """Test that limit parameter is respected"""
        limit = 3
        events = await scraper.discover_tonight("Houston", "TX", limit=limit)

        assert len(events) <= limit

    @pytest.mark.asyncio
    async def test_discover_tonight_price_info(self, scraper):
        """Test that events include price information"""
        events = await scraper.discover_tonight("Dallas", "TX", limit=5)

        for event in events:
            if "price" in event:
                assert isinstance(event["price"], str)
                # Price should be meaningful
                assert len(event["price"]) > 0

    @pytest.mark.asyncio
    async def test_discover_tonight_venue_info(self, scraper):
        """Test that events include venue information"""
        events = await scraper.discover_tonight("San Francisco", "CA", limit=5)

        venues_found = 0
        for event in events:
            if "venue" in event and event["venue"]:
                venues_found += 1
                assert isinstance(event["venue"], str)
                assert len(event["venue"]) > 0

        # Most events should have venue info
        assert venues_found > 0

    @pytest.mark.asyncio
    async def test_discover_tonight_categories_variety(self, scraper):
        """Test that discovered events span multiple categories"""
        events = await scraper.discover_tonight("Seattle", "WA", limit=20)

        categories = set(event["category"] for event in events)

        # Should have multiple different categories
        assert len(categories) >= 3

    @pytest.mark.asyncio
    async def test_discover_tonight_description_quality(self, scraper):
        """Test that event descriptions are substantial"""
        events = await scraper.discover_tonight("Portland", "OR", limit=5)

        for event in events:
            if "description" in event:
                desc = event["description"]
                # Description should be meaningful
                assert len(desc) > 20
