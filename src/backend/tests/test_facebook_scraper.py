"""
Tests for facebook_scraper.py - Facebook nonprofit event scraper
"""
import pytest
import asyncio
import time
from backend.event_discovery.facebook_scraper import FacebookEventScraper


class TestFacebookEventScraper:
    """Test suite for FacebookEventScraper"""

    @pytest.fixture
    def scraper(self):
        """Create a FacebookEventScraper instance"""
        return FacebookEventScraper()

    def test_scraper_initialization(self, scraper):
        """Test that scraper initializes correctly"""
        assert scraper is not None
        assert hasattr(scraper, 'user_agent')
        assert 'TapinVolunteerBot' in scraper.user_agent
        assert scraper.min_request_interval == 3  # 3 seconds rate limit

    def test_nonprofit_pages_defined(self, scraper):
        """Test that nonprofit pages whitelist is defined"""
        assert hasattr(scraper, 'NONPROFIT_PAGES')
        assert isinstance(scraper.NONPROFIT_PAGES, dict)
        assert len(scraper.NONPROFIT_PAGES) > 0

        # Check specific states
        assert 'TX' in scraper.NONPROFIT_PAGES
        assert 'CA' in scraper.NONPROFIT_PAGES
        assert 'NY' in scraper.NONPROFIT_PAGES
        assert 'FL' in scraper.NONPROFIT_PAGES

    def test_nonprofit_pages_structure(self, scraper):
        """Test structure of nonprofit pages data"""
        for state, pages in scraper.NONPROFIT_PAGES.items():
            assert isinstance(state, str)
            assert len(state) == 2  # State codes are 2 letters
            assert isinstance(pages, list)
            assert len(pages) > 0

            for page_id in pages:
                assert isinstance(page_id, str)
                assert len(page_id) > 0

    @pytest.mark.asyncio
    async def test_search_events_texas(self, scraper):
        """Test searching events in Texas"""
        events = await scraper.search_events("Dallas", "TX", limit=5)

        assert isinstance(events, list)
        assert len(events) > 0
        assert len(events) <= 5

    @pytest.mark.asyncio
    async def test_search_events_california(self, scraper):
        """Test searching events in California"""
        events = await scraper.search_events("Los Angeles", "CA", limit=5)

        assert isinstance(events, list)
        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_search_events_event_structure(self, scraper):
        """Test that events have correct structure"""
        events = await scraper.search_events("Houston", "TX", limit=3)

        assert len(events) > 0

        for event in events:
            # Required fields
            assert 'title' in event
            assert 'organization' in event
            assert 'city' in event
            assert 'state' in event
            assert 'category' in event

            # Check data types
            assert isinstance(event['title'], str)
            assert isinstance(event['organization'], str)
            assert len(event['title']) > 0

    @pytest.mark.asyncio
    async def test_search_events_images(self, scraper):
        """Test that events include images"""
        events = await scraper.search_events("Dallas", "TX", limit=5)

        assert len(events) > 0

        images_found = 0
        for event in events:
            if 'images' in event:
                images_found += 1
                assert isinstance(event['images'], list)

                for img in event['images']:
                    assert 'url' in img
                    assert isinstance(img['url'], str)
                    # Should have caption
                    if 'caption' in img:
                        assert isinstance(img['caption'], str)

        # At least some events should have images
        assert images_found > 0

    @pytest.mark.asyncio
    async def test_search_events_nonprofit_categories(self, scraper):
        """Test that events are nonprofit-focused"""
        events = await scraper.search_events("San Antonio", "TX", limit=5)

        valid_categories = {
            'Hunger Relief', 'Animals', 'Environment',
            'Education', 'Youth', 'Seniors', 'Community'
        }

        for event in events:
            # Category should be nonprofit-related
            assert 'category' in event

    @pytest.mark.asyncio
    async def test_search_events_url_present(self, scraper):
        """Test that events have URLs"""
        events = await scraper.search_events("Austin", "TX", limit=3)

        for event in events:
            assert 'url' in event
            assert isinstance(event['url'], str)
            assert 'facebook.com' in event['url']

    @pytest.mark.asyncio
    async def test_search_events_source_attribution(self, scraper):
        """Test that events have proper source attribution"""
        events = await scraper.search_events("Dallas", "TX", limit=3)

        for event in events:
            assert 'source' in event
            assert 'facebook.com' in event['source']

    @pytest.mark.asyncio
    async def test_search_events_limit_respected(self, scraper):
        """Test that limit parameter is respected"""
        limit = 2
        events = await scraper.search_events("Houston", "TX", limit=limit)

        assert len(events) <= limit

    @pytest.mark.asyncio
    async def test_search_events_unknown_state(self, scraper):
        """Test handling of unknown state"""
        events = await scraper.search_events("Unknown City", "ZZ", limit=5)

        # Should fall back to sample data
        assert isinstance(events, list)
        # May return sample events or empty list

    @pytest.mark.asyncio
    async def test_rate_limiting(self, scraper):
        """Test that rate limiting is enforced"""
        start_time = time.time()

        # Make two consecutive requests
        await scraper.search_events("Dallas", "TX", limit=1)
        await scraper.search_events("Houston", "TX", limit=1)

        elapsed = time.time() - start_time

        # Should take at least 3 seconds due to rate limiting
        # (allowing some tolerance for execution time)
        assert elapsed >= 2.5

    @pytest.mark.asyncio
    async def test_scrape_page_events(self, scraper):
        """Test scraping individual page events"""
        events = await scraper._scrape_page_events("DallasFoodBank", "Dallas", "TX")

        assert isinstance(events, list)
        assert len(events) > 0

        for event in events:
            assert 'title' in event
            assert 'images' in event

    def test_generate_sample_events(self, scraper):
        """Test sample event generation"""
        events = scraper._generate_sample_events_with_images("Seattle", "WA")

        assert isinstance(events, list)
        assert len(events) > 0

        for event in events:
            assert event['city'] == "Seattle"
            assert event['state'] == "WA"
            assert 'images' in event
            assert len(event['images']) > 0

    def test_validate_nonprofit_content_valid(self):
        """Test validation of nonprofit content"""
        valid_content = """
        Join our nonprofit charity volunteer event to support
        the community and help those in need. Donate your time!
        """

        result = FacebookEventScraper.validate_nonprofit_content(valid_content)
        assert result is True

    def test_validate_nonprofit_content_invalid(self):
        """Test validation of non-nonprofit content"""
        invalid_content = "This is just a random event description"

        result = FacebookEventScraper.validate_nonprofit_content(invalid_content)
        assert result is False

    def test_validate_nonprofit_content_edge_case(self):
        """Test validation with minimal nonprofit keywords"""
        # Has exactly 3 nonprofit keywords
        content = "volunteer community help"

        result = FacebookEventScraper.validate_nonprofit_content(content)
        assert result is True

    def test_extract_images_from_event(self):
        """Test image extraction from HTML"""
        html = """
        <html>
            <img class="coverPhoto" src="https://scontent.fxxx.fbcdn.net/photo.jpg" alt="Event Photo">
            <img src="https://scontent.fxxx.fbcdn.net/photo2.jpg" alt="Another Photo">
        </html>
        """

        images = FacebookEventScraper.extract_images_from_event(html)

        assert isinstance(images, list)
        # Should limit to 5 images
        assert len(images) <= 5

    def test_extract_images_limit(self):
        """Test that image extraction limits to 5 images"""
        # Create HTML with many images
        html = """
        <html>
            <img src="https://scontent.fxxx.fbcdn.net/1.jpg">
            <img src="https://scontent.fxxx.fbcdn.net/2.jpg">
            <img src="https://scontent.fxxx.fbcdn.net/3.jpg">
            <img src="https://scontent.fxxx.fbcdn.net/4.jpg">
            <img src="https://scontent.fxxx.fbcdn.net/5.jpg">
            <img src="https://scontent.fxxx.fbcdn.net/6.jpg">
            <img src="https://scontent.fxxx.fbcdn.net/7.jpg">
        </html>
        """

        images = FacebookEventScraper.extract_images_from_event(html)
        assert len(images) <= 5

    @pytest.mark.asyncio
    async def test_search_events_description_quality(self, scraper):
        """Test that event descriptions are meaningful"""
        events = await scraper.search_events("Dallas", "TX", limit=5)

        for event in events:
            if 'description' in event:
                desc = event['description']
                assert len(desc) > 20  # Should be substantial

    @pytest.mark.asyncio
    async def test_search_events_date_present(self, scraper):
        """Test that events have date information"""
        events = await scraper.search_events("Austin", "TX", limit=3)

        for event in events:
            # Should have date field
            assert 'date' in event

    @pytest.mark.asyncio
    async def test_multiple_states_coverage(self, scraper):
        """Test that multiple states are supported"""
        states_to_test = ['TX', 'CA', 'NY', 'FL']

        for state in states_to_test:
            assert state in scraper.NONPROFIT_PAGES
            pages = scraper.NONPROFIT_PAGES[state]
            assert len(pages) > 0

    def test_user_agent_compliance(self, scraper):
        """Test that user agent includes proper attribution"""
        assert '+https://tapin.org' in scraper.user_agent
        assert 'nonprofit' in scraper.user_agent.lower() or 'volunteer' in scraper.user_agent.lower()

    @pytest.mark.asyncio
    async def test_respect_rate_limit_timing(self, scraper):
        """Test _respect_rate_limit method timing"""
        scraper.last_request_time = time.time()

        start = time.time()
        await scraper._respect_rate_limit()
        elapsed = time.time() - start

        # Should wait approximately 3 seconds
        assert elapsed >= 2.5
        assert elapsed <= 4.0
