"""
LangChain-based event discovery agent for volunteer opportunities
"""
import os
import json
from typing import List, Dict
from datetime import datetime


class EventDiscoveryAgent:
    """Agent to discover and clean volunteer opportunity data"""

    def __init__(self, use_llm: bool = None):
        """
        Initialize the event discovery agent

        Args:
            use_llm: Whether to use LLM (defaults to env != 'mock')
        """
        llm_provider = os.environ.get('LLM_PROVIDER', 'openai')
        self.use_llm = use_llm if use_llm is not None else (
            llm_provider != 'mock')

        if self.use_llm:
            try:
                from langchain_openai import ChatOpenAI
                from langchain.agents import AgentExecutor, create_react_agent
                from langchain.tools import Tool
                from langchain import hub

                self.llm = ChatOpenAI(
                    model=os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
                    temperature=0.7
                )

                # Define tools for the agent
                self.tools = [
                    Tool(
                        name="search_volunteer_opportunities",
                        func=self._mock_search_opportunities,
                        description=(
                            "Search for volunteer opportunities in a given "
                            "location. Input should be a city and state."
                        )
                    ),
                    Tool(
                        name="extract_location_coords",
                        func=self._extract_coordinates,
                        description=(
                            "Extract latitude and longitude for a location. "
                            "Input should be an address or city."
                        )
                    )
                ]

                # Get ReAct prompt from hub
                prompt = hub.pull("hwchase17/react")

                # Create agent
                self.agent = create_react_agent(
                    self.llm, self.tools, prompt)
                self.agent_executor = AgentExecutor(
                    agent=self.agent,
                    tools=self.tools,
                    verbose=True,
                    handle_parsing_errors=True
                )
            except ImportError as e:
                print(f"Warning: LangChain not available - {e}")
                print("Falling back to mock mode")
                self.use_llm = False

    def discover_events(
            self, location: str, limit: int = 10) -> List[Dict]:
        """
        Discover volunteer opportunities for a location

        Args:
            location: City/region to search (e.g., "Dallas, TX")
            limit: Maximum number of events to return

        Returns:
            List of discovered events with structured data
        """
        if self.use_llm:
            return self._discover_with_llm(location, limit)
        else:
            return self._discover_mock(location, limit)

    def _discover_with_llm(
            self, location: str, limit: int) -> List[Dict]:
        """Use LangChain agent to discover events"""
        try:
            result = self.agent_executor.invoke({
                "input": (
                    f"Find {limit} volunteer opportunities in {location}. "
                    f"For each opportunity, extract: title, description, "
                    f"address, and category (Community/Animals/Environment/"
                    f"Education/Health). Return as JSON array."
                )
            })

            # Parse agent output
            output = result.get('output', '[]')
            if isinstance(output, str):
                # Try to extract JSON from the output
                import re
                json_match = re.search(r'\[.*\]', output, re.DOTALL)
                if json_match:
                    events = json.loads(json_match.group())
                else:
                    events = []
            else:
                events = output

            # Add coordinates to each event
            for event in events:
                coords = self._extract_coordinates(event.get('address', ''))
                event.update(coords)

            return events[:limit]

        except Exception as e:
            print(f"LLM discovery failed: {e}")
            print("Falling back to mock data")
            return self._discover_mock(location, limit)

    def _discover_mock(self, location: str, limit: int) -> List[Dict]:
        """Return mock volunteer opportunities for testing"""
        # Parse location
        city = location.split(',')[0].strip() if ',' in location else location

        mock_events = [
            {
                "title": f"{city} Food Bank - Volunteer Needed",
                "description": (
                    "Help sort and distribute food to families in need. "
                    "Flexible shifts available weekdays and weekends."
                ),
                "location": location,
                "category": "Community",
                "source": "mock_data"
            },
            {
                "title": f"Animal Shelter - {city}",
                "description": (
                    "Walk dogs, socialize cats, and help with adoption "
                    "events at local animal shelter."
                ),
                "location": location,
                "category": "Animals",
                "source": "mock_data"
            },
            {
                "title": f"{city} Park Cleanup Initiative",
                "description": (
                    "Join monthly park cleanup events. Help keep our "
                    "green spaces beautiful and clean."
                ),
                "location": location,
                "category": "Environment",
                "source": "mock_data"
            },
            {
                "title": f"Reading Tutor - {city} Schools",
                "description": (
                    "Tutor elementary students in reading. One hour per "
                    "week commitment. Background check required."
                ),
                "location": location,
                "category": "Education",
                "source": "mock_data"
            },
            {
                "title": f"{city} Hospital Volunteer",
                "description": (
                    "Assist hospital staff and provide comfort to "
                    "patients. Multiple departments available."
                ),
                "location": location,
                "category": "Health",
                "source": "mock_data"
            }
        ]

        # Add coordinates for each event
        for event in mock_events:
            coords = self._extract_coordinates(location)
            event.update(coords)

        return mock_events[:limit]

    def _mock_search_opportunities(self, location: str) -> str:
        """Mock search function for agent tool"""
        events = self._discover_mock(location, 5)
        return json.dumps(events, indent=2)

    def _extract_coordinates(self, location: str) -> Dict:
        """
        Extract lat/lon coordinates from location string

        For production, this would use a geocoding API.
        Currently returns mock coordinates.
        """
        # Common city coordinates (mock data)
        city_coords = {
            'dallas': (32.7767, -96.7970),
            'austin': (30.2672, -97.7431),
            'houston': (29.7604, -95.3698),
            'san antonio': (29.4241, -98.4936),
            'fort worth': (32.7555, -97.3308),
            'new york': (40.7128, -74.0060),
            'los angeles': (34.0522, -118.2437),
            'chicago': (41.8781, -87.6298),
            'miami': (25.7617, -80.1918),
            'seattle': (47.6062, -122.3321),
        }

        # Extract city name
        city = location.lower().split(',')[0].strip()

        # Find matching coordinates
        for city_key, coords in city_coords.items():
            if city_key in city:
                return {
                    'latitude': coords[0],
                    'longitude': coords[1]
                }

        # Default to Dallas if not found
        return {'latitude': 32.7767, 'longitude': -96.7970}

    def clean_and_structure(self, raw_event: Dict) -> Dict:
        """
        Clean and structure raw event data

        Args:
            raw_event: Raw event data from search/scraping

        Returns:
            Cleaned and structured event data
        """
        return {
            'title': raw_event.get('title', '').strip(),
            'description': raw_event.get('description', '').strip(),
            'location': raw_event.get('location', '').strip(),
            'latitude': raw_event.get('latitude'),
            'longitude': raw_event.get('longitude'),
            'category': self._categorize(raw_event),
            'discovered_at': datetime.utcnow().isoformat(),
            'source': raw_event.get('source', 'discovery_agent')
        }

    def _categorize(self, event: Dict) -> str:
        """
        Categorize event into one of the standard categories

        Args:
            event: Event data

        Returns:
            Category string
        """
        categories = {
            'community': ['food bank', 'homeless', 'shelter', 'community'],
            'animals': ['animal', 'pet', 'dog', 'cat', 'wildlife', 'shelter'],
            'environment': ['park', 'cleanup', 'garden', 'tree', 'river'],
            'education': ['tutor', 'mentor', 'reading', 'school', 'teach'],
            'health': ['hospital', 'medical', 'health', 'patient', 'care']
        }

        text = (
            f"{event.get('title', '')} {event.get('description', '')}"
        ).lower()

        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category.capitalize()

        return 'Community'  # Default category
