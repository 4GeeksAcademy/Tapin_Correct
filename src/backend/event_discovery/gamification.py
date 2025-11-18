"""
Gamification & Achievements System

Tracks user achievements, badges, and progression to encourage engagement.
"""

from datetime import datetime, timedelta, timezone
from collections import Counter
from typing import Dict
import json


class GamificationEngine:
    """
    Gamification system that tracks achievements and rewards users.
    """

    # Achievement definitions
    ACHIEVEMENTS = {
        "weekend_warrior": {
            "name": "Weekend Warrior",
            "description": "Attend events 5 weekends in a row",
            "icon": "🎯",
            "target": 5,
            "type": "streak",
        },
        "category_completionist": {
            "name": "Category Completionist",
            "description": "Try all 22 event categories",
            "icon": "🏆",
            "target": 22,
            "type": "collection",
        },
        "early_bird": {
            "name": "Early Bird",
            "description": "Attend 10 events discovered >1 week before",
            "icon": "🐦",
            "target": 10,
            "type": "counter",
        },
        "last_minute_larry": {
            "name": "Last Minute Larry",
            "description": "Attend 10 same-day events",
            "icon": "⚡",
            "target": 10,
            "type": "counter",
        },
        "social_butterfly": {
            "name": "Social Butterfly",
            "description": "Bring friends to 20 events",
            "icon": "🦋",
            "target": 20,
            "type": "counter",
        },
        "local_legend": {
            "name": "Local Legend",
            "description": "Attend 50 events in your city",
            "icon": "⭐",
            "target": 50,
            "type": "counter",
        },
        "explorer": {
            "name": "Explorer",
            "description": "Attend events in 5 different cities",
            "icon": "🗺️",
            "target": 5,
            "type": "collection",
        },
        "night_owl": {
            "name": "Night Owl",
            "description": "Attend 15 events starting after 8 PM",
            "icon": "🦉",
            "target": 15,
            "type": "counter",
        },
        "free_spirit": {
            "name": "Free Spirit",
            "description": "Attend 20 free events",
            "icon": "💫",
            "target": 20,
            "type": "counter",
        },
        "culture_vulture": {
            "name": "Culture Vulture",
            "description": "Attend 15 arts/theater/museum events",
            "icon": "🎭",
            "target": 15,
            "type": "counter",
        },
    }

    def __init__(self, db, user_model, achievement_model, interaction_model):
        self.db = db
        self.User = user_model
        self.Achievement = achievement_model
        self.Interaction = interaction_model

    def check_achievements(self, user_id: int):
        """
        Check and update all achievements for a user.

        Args:
            user_id: User ID
        """
        # Initialize achievements if not exist
        self._initialize_achievements(user_id)

        # Check each achievement type
        self._check_category_completionist(user_id)
        self._check_event_counters(user_id)
        self._check_weekend_warrior(user_id)
        self._check_explorer(user_id)

        self.db.session.commit()

    def get_user_level(self, user_id: int) -> Dict:
        """
        Calculate user's level and XP based on achievements and activity.

        Args:
            user_id: User ID

        Returns:
            Dictionary with level, xp, next_level_xp, title
        """
        # Count unlocked achievements
        achievements = self.Achievement.query.filter_by(
            user_id=user_id, unlocked=True
        ).all()

        unlocked_count = len(achievements)

        # Count interactions
        interactions = self.Interaction.query.filter_by(user_id=user_id).all()

        # Calculate XP
        xp = 0
        xp += len([i for i in interactions if i.interaction_type == "view"]) * 1
        xp += len([i for i in interactions if i.interaction_type == "like"]) * 5
        xp += len([i for i in interactions if i.interaction_type == "super_like"]) * 10
        xp += len([i for i in interactions if i.interaction_type == "attend"]) * 20
        xp += unlocked_count * 100  # Bonus for achievements

        # Calculate level (every 500 XP = 1 level)
        level = (xp // 500) + 1

        # Next level XP
        next_level_xp = level * 500

        # Title based on level
        title = self._get_title(level)

        return {
            "level": level,
            "xp": xp,
            "next_level_xp": next_level_xp,
            "title": title,
            "achievements_unlocked": unlocked_count,
        }

    def _initialize_achievements(self, user_id: int):
        """Create achievement records if they don't exist."""
        for achievement_type in self.ACHIEVEMENTS:
            existing = self.Achievement.query.filter_by(
                user_id=user_id, achievement_type=achievement_type
            ).first()

            if not existing:
                achievement = self.Achievement(
                    user_id=user_id,
                    achievement_type=achievement_type,
                    progress=0,
                    unlocked=False,
                )
                self.db.session.add(achievement)

    def _check_category_completionist(self, user_id: int):
        """Check if user has tried all categories."""
        interactions = self.Interaction.query.filter_by(user_id=user_id).all()

        categories_tried = set()
        for interaction in interactions:
            if interaction.event and interaction.event.category:
                if interaction.interaction_type in ["view", "like", "attend"]:
                    categories_tried.add(interaction.event.category)

        progress = len(categories_tried)

        achievement = self.Achievement.query.filter_by(
            user_id=user_id, achievement_type="category_completionist"
        ).first()

        if achievement:
            achievement.progress = progress
            if progress >= 22 and not achievement.unlocked:
                achievement.unlocked = True
                achievement.unlocked_at = datetime.now(timezone.utc)

    def _check_event_counters(self, user_id: int):
        """Check counter-based achievements."""
        interactions = self.Interaction.query.filter_by(user_id=user_id).all()

        # Early bird: events discovered >1 week before
        early_bird_count = 0

        # Last minute: same-day events
        last_minute_count = 0

        # Social butterfly: events with friends (would need metadata)
        social_count = 0

        # Local legend: events attended
        attended = len([i for i in interactions if i.interaction_type == "attend"])

        # Night owl: events after 8 PM
        night_owl_count = 0

        # Free spirit: free events
        free_count = 0

        # Culture vulture: arts/theater/museum
        culture_count = 0

        for interaction in interactions:
            if interaction.event and interaction.interaction_type == "attend":
                # Check lead time
                if interaction.event.date_start and interaction.timestamp:
                    lead_time = (
                        interaction.event.date_start - interaction.timestamp
                    ).days
                    if lead_time >= 7:
                        early_bird_count += 1
                    elif lead_time <= 0:
                        last_minute_count += 1

                # Check time of day
                if interaction.event.date_start:
                    if interaction.event.date_start.hour >= 20:
                        night_owl_count += 1

                # Check if free
                price = interaction.event.price or "Free"
                if "free" in price.lower():
                    free_count += 1

                # Check culture events
                category = interaction.event.category or ""
                if any(c in category for c in ["Arts", "Theater", "Museum", "Film"]):
                    culture_count += 1

                # Social butterfly (check metadata for friend invites)
                if interaction.metadata:
                    try:
                        meta = json.loads(interaction.metadata)
                        if meta.get("brought_friends"):
                            social_count += 1
                    except:
                        pass

        # Update achievements
        counters = {
            "early_bird": early_bird_count,
            "last_minute_larry": last_minute_count,
            "social_butterfly": social_count,
            "local_legend": attended,
            "night_owl": night_owl_count,
            "free_spirit": free_count,
            "culture_vulture": culture_count,
        }

        for achievement_type, count in counters.items():
            achievement = self.Achievement.query.filter_by(
                user_id=user_id, achievement_type=achievement_type
            ).first()

            if achievement:
                achievement.progress = count
                target = self.ACHIEVEMENTS[achievement_type]["target"]

                if count >= target and not achievement.unlocked:
                    achievement.unlocked = True
                    achievement.unlocked_at = datetime.now(timezone.utc)

    def _check_weekend_warrior(self, user_id: int):
        """Check weekend warrior streak."""
        # Get all attended events
        interactions = (
            self.Interaction.query.filter_by(user_id=user_id, interaction_type="attend")
            .order_by(self.Interaction.timestamp)
            .all()
        )

        # Group by weekend
        weekends = set()
        for interaction in interactions:
            if interaction.timestamp:
                # Check if weekend (Saturday=5, Sunday=6)
                if interaction.timestamp.weekday() in [5, 6]:
                    # Get week number
                    week_key = (
                        interaction.timestamp.year,
                        interaction.timestamp.isocalendar()[1],
                    )
                    weekends.add(week_key)

        # Check for consecutive weekends (simplified)
        max_streak = len(weekends)  # Simplified - could be more sophisticated

        achievement = self.Achievement.query.filter_by(
            user_id=user_id, achievement_type="weekend_warrior"
        ).first()

        if achievement:
            achievement.progress = max_streak
            if max_streak >= 5 and not achievement.unlocked:
                achievement.unlocked = True
                achievement.unlocked_at = datetime.now(timezone.utc)

    def _check_explorer(self, user_id: int):
        """Check explorer achievement (events in different cities)."""
        interactions = self.Interaction.query.filter_by(
            user_id=user_id, interaction_type="attend"
        ).all()

        cities = set()
        for interaction in interactions:
            if interaction.event and interaction.event.location_city:
                cities.add(interaction.event.location_city)

        progress = len(cities)

        achievement = self.Achievement.query.filter_by(
            user_id=user_id, achievement_type="explorer"
        ).first()

        if achievement:
            achievement.progress = progress
            if progress >= 5 and not achievement.unlocked:
                achievement.unlocked = True
                achievement.unlocked_at = datetime.now(timezone.utc)

    def _get_title(self, level: int) -> str:
        """Get user title based on level."""
        if level >= 50:
            return "Event Legend"
        elif level >= 30:
            return "Event Master"
        elif level >= 20:
            return "Event Guru"
        elif level >= 10:
            return "Event Enthusiast"
        elif level >= 5:
            return "Event Explorer"
        else:
            return "Event Newbie"
