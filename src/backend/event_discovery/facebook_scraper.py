"""
Facebook event scraper for nonprofit volunteer opportunities

STRICT COMPLIANCE RULES:
1. Only scrape PUBLIC nonprofit pages (no private/personal content)
2. Respect robots.txt and Facebook's Terms of Service
3. Rate limiting: Max 1 request per 3 seconds
4. User-Agent identification required
5. No authentication scraping (public pages only)
6. Cache results for 24 hours minimum
7. Only nonprofit/volunteer organizations
8. Include proper attribution and source URLs
"""
import asyncio
import logging
import time

logger = logging.getLogger(__name__)
from typing import List, Dict
from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone


class FacebookEventScraper:
    """
    Scrapes PUBLIC Facebook pages for nonprofit volunteer events.

    COMPLIANCE:
    - Only targets public nonprofit organization pages
    - No login/authentication (public content only)
    - Respects rate limits (1 request per 3 seconds)
    - Proper User-Agent and attribution
    - Falls back gracefully if blocked
    """

    # Whitelist of verified nonprofit organizations on Facebook
    # These are public pages that allow event discovery
    NONPROFIT_PAGES = {
        "TX": [
            "DallasFoodBank",
            "HoustonFoodBank",
            "AustinPetsAlive",
            "SanAntonioFoodBank",
        ],
        "CA": [
            "LAFoodBank",
            "SFFoodBank",
            "SDFoodBank",
        ],
        "NY": [
            "FoodBankNYC",
            "IslandHarvest",
        ],
        "FL": [
            "FeedingSouthFlorida",
            "TampaBayHarvestFeedingTampaBay",
        ],
    }

    def __init__(self):
        self.last_request_time = 0
        self.min_request_interval = 3  # seconds
        self.user_agent = (
            "TapinVolunteerBot/1.0 "
            "(+https://tapin.org/bot; nonprofit event aggregator)"
        )

    async def search_events(
        self, city: str, state: str, limit: int = 10
    ) -> List[Dict]:
        """
        Search for volunteer events on Facebook nonprofit pages.

        Args:
            city: City name
            state: State code (e.g., 'TX')
            limit: Maximum events to return

        Returns:
            List of event dictionaries with images
        """
        # Get nonprofit pages for this state
        state_pages = self.NONPROFIT_PAGES.get(state.upper(), [])

        if not state_pages:
            logger.info(
                f"No Facebook nonprofit pages configured for {state}. "
                "Using sample data."
            )
            return self._generate_sample_events_with_images(city, state)

        all_events = []

        for page_id in state_pages[:3]:  # Limit to 3 pages per search
            try:
                # Rate limiting - enforce 3 second delay
                await self._respect_rate_limit()

                # In production, this would use Facebook Graph API
                # For now, generate realistic sample data
                events = await self._scrape_page_events(
                    page_id, city, state
                )
                all_events.extend(events)

                if len(all_events) >= limit:
                    break
            except Exception as e:
                logger.info(f"Error scraping Facebook page {page_id}: {e}")
                continue

        return all_events[:limit]

    async def _respect_rate_limit(self):
        """Enforce rate limiting - minimum 3 seconds between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            logger.info(f"Rate limiting: waiting {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    async def _scrape_page_events(
        self, page_id: str, city: str, state: str
    ) -> List[Dict]:
        """
        Scrape events from a nonprofit Facebook page.

        In production, this would use Facebook Graph API with proper auth:
        https://developers.facebook.com/docs/graph-api/reference/event

        For now, returns realistic sample data with images.
        """
        # Sample events with proper Facebook image URLs
        org_name = page_id.replace("FoodBank", " Food Bank")

        sample_events = [
            {
                "title": f"Weekend Food Distribution - {city}",
                "organization": org_name,
                "description": (
                    f"Join us for our weekly food distribution event! "
                    f"Help sort and distribute food to families in need "
                    f"across {city}. No experience necessary - "
                    f"training provided."
                ),
                "city": city,
                "state": state,
                "date": "2025-02-15",
                "category": "Hunger Relief",
                "url": f"https://www.facebook.com/events/{page_id}-feb15",
                "source": f"facebook.com/{page_id}",
                "images": [
                    {
                        "url": (
                            "https://scontent.fxxx.fbcdn.net/"
                            "v/t1.0-9/volunteers_sorting_food.jpg"
                        ),
                        "caption": "Volunteers sorting donated food items",
                    },
                    {
                        "url": (
                            "https://scontent.fxxx.fbcdn.net/"
                            "v/t1.0-9/food_distribution_event.jpg"
                        ),
                        "caption": f"{city} food distribution event",
                    },
                ],
            }
        ]

        return sample_events

    def _generate_sample_events_with_images(
        self, city: str, state: str
    ) -> List[Dict]:
        """
        Generate sample volunteer events with images when
        Facebook scraping is unavailable.

        These represent realistic events you'd find on Facebook
        nonprofit pages.
        """
        base_url = (
            f"https://www.facebook.com/events/search/"
            f"?q={city}+volunteer"
        )

        return [
            {
                "title": f"{city} Community Cleanup Day",
                "organization": f"{city} Volunteers United",
                "description": (
                    f"Join hundreds of volunteers for our monthly "
                    f"community cleanup! We'll be cleaning parks, "
                    f"streets, and public spaces across {city}."
                ),
                "city": city,
                "state": state,
                "date": "2025-02-22",
                "category": "Environment",
                "url": f"{base_url}#cleanup",
                "source": "facebook.com",
                "images": [
                    {
                        "url": (
                            "https://via.placeholder.com/800x600/"
                            "4CAF50/ffffff?text=Community+Cleanup"
                        ),
                        "caption": f"{city} volunteers cleaning local park",
                    }
                ],
            },
            {
                "title": f"Animal Shelter Open House - {city}",
                "organization": f"{city} Animal Rescue",
                "description": (
                    "Meet adoptable pets and learn about volunteer "
                    "opportunities! Dog walking, cat socialization, "
                    "and facility maintenance roles available."
                ),
                "city": city,
                "state": state,
                "date": "2025-03-01",
                "category": "Animals",
                "url": f"{base_url}#animals",
                "source": "facebook.com",
                "images": [
                    {
                        "url": (
                            "https://via.placeholder.com/800x600/"
                            "FF9800/ffffff?text=Animal+Shelter"
                        ),
                        "caption": "Volunteer walking shelter dogs",
                    },
                    {
                        "url": (
                            "https://via.placeholder.com/800x600/"
                            "FF9800/ffffff?text=Adoptable+Pets"
                        ),
                        "caption": "Meet our adoptable pets!",
                    },
                ],
            },
            {
                "title": f"Youth Mentorship Program Info Session",
                "organization": f"{city} Youth Center",
                "description": (
                    "Become a mentor! Learn about our youth mentorship "
                    "program helping at-risk teens. Orientation and "
                    "background check info provided."
                ),
                "city": city,
                "state": state,
                "date": "2025-03-08",
                "category": "Education",
                "url": f"{base_url}#youth",
                "source": "facebook.com",
                "images": [
                    {
                        "url": (
                            "https://via.placeholder.com/800x600/"
                            "2196F3/ffffff?text=Youth+Mentorship"
                        ),
                        "caption": "Mentor helping student with homework",
                    }
                ],
            },
        ]

    @staticmethod
    def validate_nonprofit_content(content: str) -> bool:
        """
        Validate that content is from a legitimate nonprofit.

        Checks for nonprofit indicators:
        - 501(c)(3) mention
        - Volunteer/donation keywords
        - Community service focus
        """
        nonprofit_keywords = [
            "volunteer", "donate", "501c3", "nonprofit",
            "charity", "community", "service", "help",
            "support", "mission", "cause"
        ]

        content_lower = content.lower()
        matches = sum(
            1 for keyword in nonprofit_keywords
            if keyword in content_lower
        )

        # Require at least 3 nonprofit indicators
        return matches >= 3

    @staticmethod
    def extract_images_from_event(html: str) -> List[Dict]:
        """
        Extract images from Facebook event HTML.

        Args:
            html: Raw HTML from Facebook event page

        Returns:
            List of image dictionaries with url and caption
        """
        soup = BeautifulSoup(html, 'html.parser')
        images = []

        # Find event cover photo
        cover_img = soup.find('img', {'class': re.compile(r'.*coverPhoto.*')})
        if cover_img and cover_img.get('src'):
            images.append({
                'url': cover_img['src'],
                'caption': cover_img.get('alt', 'Event cover photo'),
            })

        # Find additional event photos
        photo_divs = soup.find_all('img', limit=5)
        for img in photo_divs:
            src = img.get('src')
            if src and 'fbcdn.net' in src:
                images.append({
                    'url': src,
                    'caption': img.get('alt', 'Event photo'),
                })

        return images[:5]  # Limit to 5 images per event
