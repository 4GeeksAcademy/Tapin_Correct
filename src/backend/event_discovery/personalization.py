"""
AI-Powered Personalization Engine

Tracks user preferences and behavior to provide personalized event recommendations
using collaborative filtering and content-based approaches.
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional
import json
import logging
from collections import defaultdict, Counter
import math
import asyncio
from .llm import HybridLLM

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    """
    AI-powered personalization engine that learns user preferences
    and provides personalized event recommendations.
    """

    def __init__(
        self, db, user_model, event_model, interaction_model, llm_provider=None
    ):
        """
        Initialize the personalization engine.

        Args:
            db: SQLAlchemy database instance
            user_model: User model class
            event_model: Event model class
            interaction_model: UserEventInteraction model class
            llm_provider: LLM provider (ollama, gemini, mock)
        """
        self.db = db
        self.User = user_model
        self.Event = event_model
        self.Interaction = interaction_model
        # Default provider changed to 'gemini' (Perplexity removed)
        self.llm = HybridLLM(provider=llm_provider or "gemini")

    def calculate_user_taste_profile(self, user_id: int) -> Dict:
        """
        Calculate user's taste profile based on interaction history.

        Returns:
            Dictionary with category preferences, time preferences, etc.
        """
        interactions = self.Interaction.query.filter_by(user_id=user_id).all()

        if not interactions:
            return self._default_profile()

        # Category preferences (based on positive interactions)
        category_scores = Counter()
        for interaction in interactions:
            if interaction.interaction_type in ["view", "like", "attend"]:
                weight = self._interaction_weight(interaction.interaction_type)
                category_scores[interaction.event.category] += weight

        # Normalize scores
        total = sum(category_scores.values())
        category_preferences = (
            {cat: score / total for cat, score in category_scores.items()}
            if total > 0
            else {}
        )

        # Time preferences (when user typically looks for events)
        hour_preferences = self._calculate_time_preferences(interactions)

        # Price sensitivity
        price_sensitivity = self._calculate_price_sensitivity(interactions)

        # Adventure level (willingness to try new categories)
        adventure_level = self._calculate_adventure_level(interactions)

        return {
            "category_preferences": category_preferences,
            "hour_preferences": hour_preferences,
            "price_sensitivity": price_sensitivity,
            "adventure_level": adventure_level,
            "favorite_venues": self._get_favorite_venues(interactions),
            "average_lead_time": self._calculate_lead_time(interactions),
        }

    def get_personalized_feed(
        self, user_id: int, events: List, limit: int = 20
    ) -> List[Dict]:
        """
        Generate personalized feed for user with confidence scores.

        Args:
            user_id: User ID
            events: List of event dictionaries
            limit: Maximum number of events to return

        Returns:
            List of events with match_score and explanation
        """
        profile = self.calculate_user_taste_profile(user_id)

        # Score each event
        scored_events = []
        for event in events:
            score, explanation = self._score_event(event, profile)
            scored_events.append(
                {
                    **event,
                    "match_score": score,
                    "match_explanation": explanation,
                    "confidence": self._calculate_confidence(score, profile),
                }
            )

        # Sort by score
        scored_events.sort(key=lambda x: x["match_score"], reverse=True)

        return scored_events[:limit]

    def record_interaction(
        self,
        user_id: int,
        event_id: str,
        interaction_type: str,
        metadata: Optional[Dict] = None,
    ):
        """
        Record user interaction with an event.

        Args:
            user_id: User ID
            event_id: Event ID
            interaction_type: Type of interaction (view, like, dislike, attend, skip)
            metadata: Additional metadata (e.g., time_spent, swipe_direction)
        """
        interaction = self.Interaction(
            user_id=user_id,
            event_id=event_id,
            interaction_type=interaction_type,
            metadata=json.dumps(metadata) if metadata else None,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.session.add(interaction)
        self.db.session.commit()

    def get_similar_users(self, user_id: int, limit: int = 10) -> List[int]:
        """
        Find similar users based on interaction patterns (collaborative filtering).

        Args:
            user_id: User ID
            limit: Number of similar users to return

        Returns:
            List of similar user IDs
        """
        # Get user's liked events
        user_likes = set(
            i.event_id
            for i in self.Interaction.query.filter_by(
                user_id=user_id, interaction_type="like"
            ).all()
        )

        if not user_likes:
            return []

        # Find users with overlapping likes
        all_users = self.User.query.all()
        similarity_scores = []

        for other_user in all_users:
            if other_user.id == user_id:
                continue

            other_likes = set(
                i.event_id
                for i in self.Interaction.query.filter_by(
                    user_id=other_user.id, interaction_type="like"
                ).all()
            )

            if not other_likes:
                continue

            # Jaccard similarity
            intersection = len(user_likes & other_likes)
            union = len(user_likes | other_likes)
            similarity = intersection / union if union > 0 else 0

            if similarity > 0:
                similarity_scores.append((other_user.id, similarity))

        # Sort by similarity
        similarity_scores.sort(key=lambda x: x[1], reverse=True)

        return [user_id for user_id, _ in similarity_scores[:limit]]

    def get_collaborative_recommendations(
        self, user_id: int, limit: int = 10
    ) -> List[str]:
        """
        Get recommendations based on what similar users liked.

        Args:
            user_id: User ID
            limit: Number of recommendations

        Returns:
            List of recommended event IDs
        """
        similar_users = self.get_similar_users(user_id, limit=20)

        if not similar_users:
            return []

        # Get user's already interacted events
        user_events = set(
            i.event_id for i in self.Interaction.query.filter_by(user_id=user_id).all()
        )

        # Get events liked by similar users
        recommendation_scores = Counter()

        for similar_user_id in similar_users:
            likes = self.Interaction.query.filter_by(
                user_id=similar_user_id, interaction_type="like"
            ).all()

            for like in likes:
                if like.event_id not in user_events:
                    recommendation_scores[like.event_id] += 1

        # Return top recommendations
        top_recommendations = [
            event_id for event_id, _ in recommendation_scores.most_common(limit)
        ]

        return top_recommendations

    # Private helper methods

    def _default_profile(self) -> Dict:
        """Return default profile for new users."""
        return {
            "category_preferences": {},
            "hour_preferences": {},
            "price_sensitivity": "medium",
            "adventure_level": 0.5,
            "favorite_venues": [],
            "average_lead_time": 7,  # days
        }

    def _interaction_weight(self, interaction_type: str) -> float:
        """Weight different interaction types."""
        weights = {
            "view": 1.0,
            "like": 3.0,
            "super_like": 5.0,
            "attend": 10.0,
            "dislike": -2.0,
            "skip": -0.5,
        }
        return weights.get(interaction_type, 0.0)

    def _score_event(self, event: Dict, profile: Dict) -> tuple:
        """
        Score an event based on user profile.

        Returns:
            (score, explanation) tuple
        """
        score = 0.0
        reasons = []

        # Category match
        category = event.get("category", "")
        if category in profile["category_preferences"]:
            cat_score = profile["category_preferences"][category] * 50
            score += cat_score
            if cat_score > 10:
                reasons.append(f"Matches your interest in {category}")

        # Price match
        price = event.get("price", "Free")
        if self._price_matches_sensitivity(price, profile["price_sensitivity"]):
            score += 10
            if "free" in price.lower():
                reasons.append("Free event")

        # Venue match
        venue = event.get("venue", "")
        if venue in profile["favorite_venues"]:
            score += 15
            reasons.append(f"At one of your favorite venues")

        # Image quality (events with images score higher)
        if event.get("image_url"):
            score += 5

        # Recency boost
        if event.get("scraped_at"):
            score += 5
            reasons.append("Recently added")

        # Base score
        score += 20

        explanation = " • ".join(reasons[:3]) if reasons else "New recommendation"

        return min(score, 100), explanation

    def _calculate_confidence(self, score: float, profile: Dict) -> int:
        """Calculate confidence percentage (0-100)."""
        # Higher confidence if we have more data about user
        data_points = len(profile.get("category_preferences", {}))
        data_confidence = min(data_points * 10, 30)

        # Score-based confidence
        score_confidence = score * 0.7

        return int(data_confidence + score_confidence)

    def _calculate_time_preferences(self, interactions) -> Dict:
        """Calculate what times user typically looks for events."""
        hours = [i.timestamp.hour for i in interactions if i.timestamp]
        hour_counts = Counter(hours)
        total = len(hours)

        return (
            {hour: count / total for hour, count in hour_counts.items()}
            if total > 0
            else {}
        )

    def _calculate_price_sensitivity(self, interactions) -> str:
        """Determine user's price sensitivity."""
        # Look at price of events user attended/liked
        prices = []
        for i in interactions:
            if i.interaction_type in ["like", "attend"] and i.event:
                price_str = i.event.price or "Free"
                if "free" in price_str.lower():
                    prices.append(0)
                # Could parse actual prices here

        avg_price = sum(prices) / len(prices) if prices else 0

        if avg_price == 0:
            return "low"
        elif avg_price < 20:
            return "medium"
        else:
            return "high"

    def _calculate_adventure_level(self, interactions) -> float:
        """Calculate how adventurous user is (0-1)."""
        if not interactions:
            return 0.5

        categories_tried = set(
            i.event.category
            for i in interactions
            if i.event and i.interaction_type in ["view", "like", "attend"]
        )

        # More categories = more adventurous
        return min(len(categories_tried) / 10, 1.0)

    def _get_favorite_venues(self, interactions, limit=5) -> List[str]:
        """Get user's favorite venues."""
        venue_counts = Counter()

        for i in interactions:
            if i.event and i.event.venue and i.interaction_type in ["like", "attend"]:
                venue_counts[i.event.venue] += 1

        return [venue for venue, _ in venue_counts.most_common(limit)]

    def _calculate_lead_time(self, interactions) -> int:
        """Calculate average lead time (days between discovery and event)."""
        lead_times = []

        for i in interactions:
            if i.event and i.event.date_start and i.timestamp:
                lead_time = (i.event.date_start - i.timestamp).days
                if 0 <= lead_time <= 365:  # Reasonable range
                    lead_times.append(lead_time)

        return int(sum(lead_times) / len(lead_times)) if lead_times else 7

    def _price_matches_sensitivity(self, price: str, sensitivity: str) -> bool:
        """Check if price matches user's sensitivity."""
        if "free" in price.lower():
            return True  # Everyone likes free

        if sensitivity == "low":
            return "free" in price.lower()
        elif sensitivity == "medium":
            return True  # Medium accepts anything
        else:  # high
            return True  # High spenders accept anything

        return True

    async def get_ai_personalized_recommendations(
        self, user_id: int, events: List[Dict], limit: int = 10
    ) -> List[Dict]:
        """
        Use AI (HybridLLM) to generate highly personalized event recommendations
        with natural language explanations.

        Args:
            user_id: User ID
            events: List of candidate events
            limit: Number of recommendations to return

        Returns:
            List of events with AI-generated match scores and explanations
        """
        # Get user profile
        profile = self.calculate_user_taste_profile(user_id)

        # Get recent interactions for context
        recent_interactions = (
            self.Interaction.query.filter_by(user_id=user_id)
            .order_by(self.Interaction.timestamp.desc())
            .limit(10)
            .all()
        )

        # Build context for AI
        liked_events = []
        disliked_events = []

        for interaction in recent_interactions:
            if interaction.event:
                event_desc = f"{interaction.event.title} ({interaction.event.category})"
                if interaction.interaction_type in ["like", "super_like", "attend"]:
                    liked_events.append(event_desc)
                elif interaction.interaction_type == "dislike":
                    disliked_events.append(event_desc)

        # Prepare candidate events (top 20 by basic scoring)
        scored_events = []
        for event in events[:50]:  # Limit to top 50 candidates
            score, _ = self._score_event(event, profile)
            scored_events.append((score, event))

        scored_events.sort(reverse=True, key=lambda x: x[0])
        candidates = [event for _, event in scored_events[:20]]

        # Build prompt for AI
        prompt = self._build_personalization_prompt(
            profile, liked_events, disliked_events, candidates, limit
        )

        try:
            # Call AI
            response = await self.llm.ainvoke(prompt)
            ai_recommendations = self._parse_ai_response(response.content, candidates)

            if ai_recommendations:
                return ai_recommendations[:limit]
        except Exception as e:
            logger.error(f"AI personalization error: {e}")

        # Fallback to basic personalization
        return self.get_personalized_feed(user_id, events, limit)

    def _build_personalization_prompt(
        self,
        profile: Dict,
        liked_events: List[str],
        disliked_events: List[str],
        candidates: List[Dict],
        limit: int,
    ) -> str:
        """Build prompt for AI personalization."""
        liked_str = (
            "\n".join(f"- {e}" for e in liked_events[:5])
            if liked_events
            else "None yet"
        )
        disliked_str = (
            "\n".join(f"- {e}" for e in disliked_events[:5])
            if disliked_events
            else "None"
        )

        categories_str = (
            ", ".join(
                f"{cat} ({score:.0f}%)"
                for cat, score in sorted(
                    profile["category_preferences"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]
            )
            if profile["category_preferences"]
            else "Still learning preferences"
        )

        candidates_str = ""
        for i, event in enumerate(candidates[:15], 1):
            candidates_str += f"\n{i}. {event.get('title', 'Untitled')} - {event.get('category', 'Unknown')} at {event.get('venue', 'TBD')}"
            if event.get("description"):
                desc = event["description"][:100]
                candidates_str += f"\n   Description: {desc}..."

        prompt = f"""You are an expert event recommendation AI. Analyze this user's preferences and recommend the {limit} best events from the candidates below.

USER PROFILE:
- Favorite Categories: {categories_str}
- Price Sensitivity: {profile.get('price_sensitivity', 'medium')}
- Adventure Level: {profile.get('adventure_level', 0.5):.0%}
- Typical Planning Lead Time: {profile.get('average_lead_time', 7)} days

EVENTS THEY LIKED:
{liked_str}

EVENTS THEY DISLIKED:
{disliked_str}

CANDIDATE EVENTS:
{candidates_str}

TASK: Select the top {limit} events that best match this user's preferences. For each, provide:
1. Event number (from candidates list)
2. Match score (0-100)
3. Brief explanation (1-2 sentences) of why it's a good match

Return ONLY a valid JSON array like this:
[
  {{"event_num": 1, "match_score": 95, "explanation": "Perfect match because..."}},
  {{"event_num": 3, "match_score": 88, "explanation": "Great fit since..."}}
]

Respond with ONLY the JSON array, no other text."""

        return prompt

    def _parse_ai_response(
        self, response_text: str, candidates: List[Dict]
    ) -> List[Dict]:
        """Parse AI response and attach recommendations to events."""
        try:
            # Extract JSON from response
            response_text = response_text.strip()

            # Find JSON array in response
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]") + 1

            if start_idx == -1 or end_idx == 0:
                return []

            json_str = response_text[start_idx:end_idx]
            recommendations = json.loads(json_str)

            if not isinstance(recommendations, list):
                return []

            # Attach AI recommendations to events
            result = []
            for rec in recommendations:
                if not isinstance(rec, dict):
                    continue

                event_num = rec.get("event_num")
                if event_num is None or event_num < 1 or event_num > len(candidates):
                    continue

                # Get the corresponding event (1-indexed)
                event = candidates[event_num - 1].copy()
                event["ai_match_score"] = rec.get("match_score", 50)
                event["ai_explanation"] = rec.get(
                    "explanation", "AI-recommended for you"
                )

                result.append(event)

            return result

        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return []
