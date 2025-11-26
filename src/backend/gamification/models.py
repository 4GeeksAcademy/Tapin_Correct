"""
Gamification-specific database models.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    JSON,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from datetime import datetime


def create_gamification_models(db):
    """
    Factory function for gamification models
    """

    class Achievement(db.Model):
        __tablename__ = "achievements"

        id = Column(Integer, primary_key=True)
        name = Column(String(100), nullable=False, unique=True)
        description = Column(Text)
        icon_url = Column(String(500))
        category = Column(String(50))
        criteria = Column(JSON, nullable=False)
        points = Column(Integer, default=0)
        created_at = Column(DateTime, default=datetime.utcnow)

        def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "icon_url": self.icon_url,
                "category": self.category,
                "criteria": self.criteria,
                "points": self.points,
            }

    class UserAchievement(db.Model):
        __tablename__ = "user_achievements"

        id = Column(Integer, primary_key=True)
        volunteer_id = Column(
            Integer, ForeignKey("volunteer_profiles.id"), nullable=False
        )
        achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
        unlocked_at = Column(DateTime, default=datetime.utcnow)
        progress = Column(JSON, default=dict)

        __table_args__ = (
            UniqueConstraint(
                "volunteer_id", "achievement_id", name="unique_user_achievement"
            ),
        )

        def to_dict(self):
            return {
                "id": self.id,
                "achievement_id": self.achievement_id,
                "unlocked_at": self.unlocked_at.isoformat(),
                "progress": self.progress,
            }

    return Achievement, UserAchievement
