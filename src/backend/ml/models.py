"""
ML-specific database models.
Add these to your existing `models.py` or keep separate and import as needed.
"""

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from datetime import datetime


def create_ml_models(db):
    """
    Factory function to create ML models on the provided SQLAlchemy `db` object.
    Call `create_ml_models(db)` from your main models module if you want
    to attach these models to the same metadata.
    """

    class TasteProfile(db.Model):
        __tablename__ = "taste_profiles"

        id = Column(Integer, primary_key=True)
        volunteer_id = Column(
            Integer, ForeignKey("volunteer_profiles.id"), unique=True, nullable=False
        )

        # ML-Generated Preferences
        category_preferences = Column(JSON, default=dict)
        location_preferences = Column(JSON, default=dict)
        time_preferences = Column(JSON, default=dict)

        # Personality Metrics (0-1 scale)
        adventure_level = Column(Float, default=0.5)
        social_preference = Column(Float, default=0.5)
        commitment_level = Column(Float, default=0.5)

        # Settings
        price_sensitivity = Column(String(20), default="medium")

        # Versioning
        model_version = Column(String(20), default="v1.0")
        last_updated = Column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

        def to_dict(self):
            return {
                "category_preferences": self.category_preferences or {},
                "adventure_level": self.adventure_level,
                "social_preference": self.social_preference,
                "price_sensitivity": self.price_sensitivity,
                "last_updated": (
                    self.last_updated.isoformat() if self.last_updated else None
                ),
            }

    return TasteProfile
