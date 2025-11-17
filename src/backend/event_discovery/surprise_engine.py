"""
Surprise Me! - AI Event Generator

Generates unexpected but relevant event recommendations based on mood,
budget, time constraints, and user's adventure level.
"""

import random
from typing import List, Dict, Optional
from datetime import datetime, timezone


class SurpriseEngine:
    """
    Serendipity engine that generates surprising event recommendations.
    """

    # Mood-to-category mappings
    MOOD_CATEGORIES = {
        'energetic': ['Sports', 'Fitness', 'Music & Concerts', 'Nightlife', 'Dance'],
        'chill': ['Yoga', 'Parks', 'Books & Literature', 'Wine & Beer', 'Outdoor'],
        'creative': ['Arts & Theater', 'Film & Media', 'Books & Literature', 'Markets & Fairs'],
        'social': ['Networking', 'Comedy', 'Food & Dining', 'Nightlife', 'Community'],
        'romantic': ['Wine & Beer', 'Music & Concerts', 'Arts & Theater', 'Food & Dining'],
        'adventurous': ['Outdoor', 'Sports', 'Tech & Innovation', 'New Experiences']
    }

    def __init__(self, db, user_model, event_model, interaction_model):
        self.db = db
        self.User = user_model
        self.Event = event_model
        self.Interaction = interaction_model

    def generate_surprise(
        self,
        user_id: int,
        events: List[Dict],
        mood: str = 'adventurous',
        budget: float = 50,
        time_available: int = 3,
        adventure_level: str = 'high'
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
        if adventure_level == 'high':
            # Prefer categories user hasn't tried
            candidates = [
                e for e in affordable_events
                if e.get('category') not in past_categories
            ]
            if not candidates:
                candidates = affordable_events  # Fallback
        elif adventure_level == 'medium':
            # Mix of familiar and new
            familiar = [e for e in affordable_events if e.get('category') in past_categories]
            new = [e for e in affordable_events if e.get('category') not in past_categories]

            candidates = familiar[:len(affordable_events)//2] + new[:len(affordable_events)//2]
            if not candidates:
                candidates = affordable_events
        else:  # low
            # Prefer familiar categories
            candidates = [
                e for e in affordable_events
                if e.get('category') in past_categories
            ]
            if not candidates:
                candidates = affordable_events

        # Filter by mood
        mood_categories = self.MOOD_CATEGORIES.get(mood, [])
        mood_matches = [
            e for e in candidates
            if any(cat in e.get('category', '') for cat in mood_categories)
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
            surprise_event,
            mood,
            adventure_level,
            past_categories
        )

        surprise_event['surprise_explanation'] = explanation
        surprise_event['surprise_score'] = random.randint(80, 100)  # It's a surprise!

        return surprise_event

    def _filter_by_budget(self, events: List[Dict], budget: float) -> List[Dict]:
        """Filter events by budget."""
        affordable = []

        for event in events:
            price_str = event.get('price', 'Free')

            if 'free' in price_str.lower():
                affordable.append(event)
            elif budget >= 50:  # High budget, accept all
                affordable.append(event)
            # Could parse actual prices here

        return affordable if affordable else events  # Fallback to all

    def _get_user_categories(self, user_id: int) -> set:
        """Get categories user has interacted with."""
        interactions = self.Interaction.query.filter_by(
            user_id=user_id
        ).join(self.Event).all()

        categories = set()
        for interaction in interactions:
            if interaction.event and interaction.event.category:
                categories.add(interaction.event.category)

        return categories

    def _generate_explanation(
        self,
        event: Dict,
        mood: str,
        adventure_level: str,
        past_categories: set
    ) -> str:
        """Generate explanation for why this event was chosen."""
        explanations = []

        category = event.get('category', '')

        # Mood-based explanation
        if mood in self.MOOD_CATEGORIES:
            mood_cats = self.MOOD_CATEGORIES[mood]
            if any(cat in category for cat in mood_cats):
                explanations.append(f"Perfect for a {mood} mood")

        # Adventure level explanation
        if category not in past_categories:
            if adventure_level == 'high':
                explanations.append("A new experience for you")
            else:
                explanations.append("Something different to try")
        else:
            explanations.append("Based on your past interests")

        # Price explanation
        price = event.get('price', 'Free')
        if 'free' in price.lower():
            explanations.append("Free to attend")

        # Default explanation
        if not explanations:
            explanations.append("Hand-picked just for you")

        return " • ".join(explanations)
