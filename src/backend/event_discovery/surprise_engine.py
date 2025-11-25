"""
Surprise Me! - AI Event Generator

Generates unexpected but relevant event recommendations based on mood,
budget, time constraints, and user's adventure level.
"""

import random
from typing import List, Dict, Optional
from datetime import datetime, timezone
import asyncio
import json
from .llm import HybridLLM


class SurpriseEngine:
    """
    Serendipity engine that generates surprising event recommendations.
    """

    # Mood-to-category mappings
    MOOD_CATEGORIES = {
        "energetic": ["Sports", "Fitness", "Music & Concerts", "Nightlife", "Dance"],
        "chill": ["Yoga", "Parks", "Books & Literature", "Wine & Beer", "Outdoor"],
        "creative": [
            "Arts & Theater",
            "Film & Media",
            "Books & Literature",
            "Markets & Fairs",
        ],
        "social": ["Networking", "Comedy", "Food & Dining", "Nightlife", "Community"],
        "romantic": [
            "Wine & Beer",
            "Music & Concerts",
            "Arts & Theater",
            "Food & Dining",
        ],
        "adventurous": ["Outdoor", "Sports", "Tech & Innovation", "New Experiences"],
    }

    def __init__(
        self, db, user_model, event_model, interaction_model, llm_provider=None
    ):
        self.db = db
        self.User = user_model
        # Default provider changed to 'gemini' (Perplexity removed)
        self.llm = HybridLLM(provider=llm_provider or "gemini")
        self.Event = event_model
        self.Interaction = interaction_model

    def generate_surprise(
        self,
        user_id: int,
        events: List[Dict],
        mood: str = "adventurous",
        budget: float = 50,
        time_available: int = 3,
        adventure_level: str = "high",
    ) -> Optional[Dict]:
        """
        Generate a surprise event recommendation.

        Args:
            user_id: User ID
            events: List of available events
            mood: User's current mood
            budget: Maximum budget
            time_available: Hours available
            adventure_level: How adventurous (low/medium/high)

        Returns:
            Surprise event with explanation
        """
        if not events:
            return None

        # Filter by budget
        affordable_events = self._filter_by_budget(events, budget)

        if not affordable_events:
            return None

        # Get user's history
        past_categories = self._get_user_categories(user_id)

        # Filter based on adventure level
        if adventure_level == "high":
            # Prefer categories user hasn't tried
            candidates = [
                e for e in affordable_events if e.get("category") not in past_categories
            ]
            if not candidates:
                candidates = affordable_events  # Fallback
        elif adventure_level == "medium":
            # Mix of familiar and new
            familiar = [
                e for e in affordable_events if e.get("category") in past_categories
            ]
            new = [
                e for e in affordable_events if e.get("category") not in past_categories
            ]

            candidates = (
                familiar[: len(affordable_events) // 2]
                + new[: len(affordable_events) // 2]
            )
            if not candidates:
                candidates = affordable_events
        else:  # low
            # Prefer familiar categories
            candidates = [
                e for e in affordable_events if e.get("category") in past_categories
            ]
            if not candidates:
                candidates = affordable_events

        # Filter by mood
        mood_categories = self.MOOD_CATEGORIES.get(mood, [])
        mood_matches = [
            e
            for e in candidates
            if any(cat in e.get("category", "") for cat in mood_categories)
        ]

        # Choose final candidates
        if mood_matches:
            final_candidates = mood_matches
        else:
            final_candidates = candidates

        if not final_candidates:
            return None

        # Select random surprise event
        surprise_event = random.choice(final_candidates)

        # Generate explanation
        explanation = self._generate_explanation(
            surprise_event, mood, adventure_level, past_categories
        )

        surprise_event["surprise_explanation"] = explanation
        surprise_event["surprise_score"] = random.randint(80, 100)  # It's a surprise!

        return surprise_event

    def _filter_by_budget(self, events: List[Dict], budget: float) -> List[Dict]:
        """Filter events by budget."""
        affordable = []

        for event in events:
            price_str = event.get("price", "Free")

            if "free" in price_str.lower():
                affordable.append(event)
            elif budget >= 50:  # High budget, accept all
                affordable.append(event)
            # Could parse actual prices here

        return affordable if affordable else events  # Fallback to all

    def _get_user_categories(self, user_id: int) -> set:
        """Get categories user has interacted with."""
        interactions = (
            self.Interaction.query.filter_by(user_id=user_id).join(self.Event).all()
        )

        categories = set()
        for interaction in interactions:
            if interaction.event and interaction.event.category:
                categories.add(interaction.event.category)

        return categories

    def _generate_explanation(
        self, event: Dict, mood: str, adventure_level: str, past_categories: set
    ) -> str:
        """Generate explanation for why this event was chosen."""
        explanations = []

        category = event.get("category", "")

        # Mood-based explanation
        if mood in self.MOOD_CATEGORIES:
            mood_cats = self.MOOD_CATEGORIES[mood]
            if any(cat in category for cat in mood_cats):
                explanations.append(f"Perfect for a {mood} mood")

        # Adventure level explanation
        if category not in past_categories:
            if adventure_level == "high":
                explanations.append("A new experience for you")
            else:
                explanations.append("Something different to try")
        else:
            explanations.append("Based on your past interests")

        # Price explanation
        price = event.get("price", "Free")
        if "free" in price.lower():
            explanations.append("Free to attend")

        # Default explanation
        if not explanations:
            explanations.append("Hand-picked just for you")

        return " • ".join(explanations)

    async def generate_ai_surprise(
        self,
        user_id: int,
        location: str,
        mood: str = "adventurous",
        budget: float = 50.0,
        time_available: int = 120,
        adventure_level: str = "medium",
    ) -> Optional[Dict]:
        """
        Use AI (HybridLLM) to generate a truly surprising and personalized
        event recommendation.

        Args:
            user_id: User ID
            location: City/location
            mood: Current mood
            budget: Budget in dollars
            time_available: Available time in minutes
            adventure_level: How adventurous (low/medium/high)

        Returns:
            Surprise event with AI-generated explanation, or None
        """
        # Get all available events
        events = self.Event.query.filter_by(location_city=location).all()

        if not events:
            return None

        # Convert to dict for easier processing
        events_list = []
        for event in events:
            events_list.append(
                {
                    "id": event.id,
                    "title": event.title,
                    "category": event.category,
                    "description": event.description or "",
                    "venue": event.venue,
                    "price": event.price or "Free",
                    "date_start": str(event.date_start) if event.date_start else "TBD",
                    "image_url": event.image_url,
                }
            )

        # Get user's past interactions
        interactions = self.Interaction.query.filter_by(user_id=user_id).all()
        past_events = []
        liked_categories = set()

        for interaction in interactions:
            if interaction.event:
                if interaction.interaction_type in ["like", "super_like", "attend"]:
                    past_events.append(
                        f"{interaction.event.title} ({interaction.event.category})"
                    )
                    liked_categories.add(interaction.event.category)

        # Build AI prompt
        prompt = self._build_surprise_prompt(
            mood,
            budget,
            time_available,
            adventure_level,
            past_events,
            liked_categories,
            events_list,
        )

        try:
            # Call AI
            response = await self.llm.ainvoke(prompt)
            surprise_event = self._parse_surprise_response(
                response.content, events_list
            )

            if surprise_event:
                return surprise_event
        except Exception as e:
            print(f"AI surprise error: {e}")

        # Fallback to basic surprise generation
        return self.generate_surprise(
            user_id, events_list, mood, budget, time_available, adventure_level
        )

    def _build_surprise_prompt(
        self,
        mood: str,
        budget: float,
        time_available: int,
        adventure_level: str,
        past_events: List[str],
        liked_categories: set,
        candidates: List[Dict],
    ) -> str:
        """Build AI prompt for surprise generation."""
        past_str = (
            "\n".join(f"- {e}" for e in past_events[:10])
            if past_events
            else "No history yet"
        )
        liked_cats_str = ", ".join(liked_categories) if liked_categories else "None yet"

        # Select 20 random candidates for variety
        sample_candidates = random.sample(candidates, min(20, len(candidates)))

        candidates_str = ""
        for i, event in enumerate(sample_candidates, 1):
            candidates_str += f"\n{i}. {event.get('title')} - {event.get('category')} at {event.get('venue')}"
            if event.get("description"):
                desc = event["description"][:80]
                candidates_str += f"\n   {desc}..."
            candidates_str += f"\n   Price: {event.get('price', 'Free')}"

        prompt = f"""You are a serendipity AI that generates delightful, unexpected event recommendations.

USER CONTEXT:
- Current Mood: {mood}
- Budget: ${budget}
- Available Time: {time_available} minutes
- Adventure Level: {adventure_level}
- Previously Liked Categories: {liked_cats_str}

PAST EVENTS THEY ENJOYED:
{past_str}

CANDIDATE EVENTS:
{candidates_str}

TASK: Pick ONE event that will be a delightful surprise - something they might not expect but will love. Consider:
1. If adventure_level is HIGH: Choose something completely different from their past
2. If adventure_level is LOW: Choose something similar but with a twist
3. Match their current mood and constraints
4. Think outside the box - surprise them!

Return ONLY a valid JSON object like this:
{{
  "event_num": 5,
  "surprise_score": 92,
  "explanation": "A creative 2-3 sentence explanation of why this is a perfect surprise for them"
}}

Respond with ONLY the JSON object, no other text."""

        return prompt

    def _parse_surprise_response(
        self, response_text: str, candidates: List[Dict]
    ) -> Optional[Dict]:
        """Parse AI surprise response."""
        try:
            # Extract JSON from response
            response_text = response_text.strip()

            # Find JSON object in response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                return None

            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)

            if not isinstance(result, dict):
                return None

            event_num = result.get("event_num")
            if event_num is None or event_num < 1 or event_num > len(candidates):
                return None

            # Get the event (1-indexed)
            event = candidates[event_num - 1].copy()
            event["surprise_score"] = result.get("surprise_score", 85)
            event["surprise_explanation"] = result.get(
                "explanation", "AI-picked surprise for you!"
            )

            return event

        except Exception as e:
            print(f"Error parsing surprise response: {e}")
            return None
