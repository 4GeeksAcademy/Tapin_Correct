from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models import (
    db,
    UserEventInteraction,
    TasteProfile,
    InteractionType,
    VolunteerProfile,
)


class TasteProfileGenerator:
    """
    Generates personalized taste profiles based on user interaction history.
    Uses simple frequency analysis and weighted scoring.
    """

    def __init__(self, volunteer_id):
        self.volunteer_id = volunteer_id
        self.interactions = self._fetch_interactions()

    def _fetch_interactions(self):
        """Get last 90 days of interactions"""
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        return (
            UserEventInteraction.query.filter(
                UserEventInteraction.user_id == self.volunteer_id,
                UserEventInteraction.timestamp >= cutoff_date,
            )
            .order_by(UserEventInteraction.timestamp.desc())
            .all()
        )

    def generate_profile(self):
        """Generate complete taste profile"""
        if not self.interactions:
            return self._default_profile()

        category_prefs = self._calculate_category_preferences()
        adventure_level = self._calculate_adventure_level()
        social_pref = self._calculate_social_preference()

        # Update or create taste profile
        profile = TasteProfile.query.filter_by(volunteer_id=self.volunteer_id).first()
        if not profile:
            profile = TasteProfile(volunteer_id=self.volunteer_id)
            db.session.add(profile)

        profile.category_preferences = category_prefs
        profile.adventure_level = adventure_level
        profile.social_preference = social_pref
        profile.last_updated = datetime.utcnow()

        db.session.commit()
        return profile

    def _calculate_category_preferences(self):
        """
        Calculate preference score for each category based on:
        - Number of likes vs dislikes
        - Recency of interactions
        - Registration/attendance (strongest signal)
        """
        category_scores = defaultdict(
            lambda: {"likes": 0, "dislikes": 0, "registers": 0, "score": 0}
        )

        for interaction in self.interactions:
            cat = interaction.category or "uncategorized"

            # Weight by interaction type
            if interaction.interaction_type == InteractionType.LIKE:
                category_scores[cat]["likes"] += 1
            elif interaction.interaction_type == InteractionType.DISLIKE:
                category_scores[cat]["dislikes"] += 0.5
            elif interaction.interaction_type == InteractionType.REGISTER:
                category_scores[cat]["registers"] += 3

        # Calculate normalized scores (0-1)
        max_score = 0
        for cat, data in category_scores.items():
            raw_score = data["likes"] + data["registers"] * 2 - data["dislikes"]
            data["score"] = max(0, raw_score)
            max_score = max(max_score, data["score"])

        # Normalize
        normalized = {}
        for cat, data in category_scores.items():
            if max_score > 0:
                normalized[cat] = round(data["score"] / max_score, 2)
            else:
                normalized[cat] = 0

        return dict(sorted(normalized.items(), key=lambda x: x[1], reverse=True))

    def _calculate_adventure_level(self):
        """
        Calculate how adventurous the user is (trying new categories)
        0 = Always same categories, 1 = Loves variety
        """
        if not self.interactions:
            return 0.5

        categories_interacted = set(i.category for i in self.interactions if i.category)
        unique_ratio = len(categories_interacted) / max(len(self.interactions), 1)

        # Scale to 0-1 (assume >5 unique categories = very adventurous)
        return min(unique_ratio * 2, 1.0)

    def _calculate_social_preference(self):
        """
        Placeholder for social preference analysis.
        Would analyze: group size, team events, etc.
        """
        return 0.5

    def _default_profile(self):
        """Return default profile for new users"""
        profile = TasteProfile(
            volunteer_id=self.volunteer_id,
            category_preferences={},
            adventure_level=0.5,
            social_preference=0.5,
            price_sensitivity="medium",
        )
        db.session.add(profile)
        db.session.commit()
        return profile


# API Endpoint integration (lightweight)
ml_api = Blueprint("ml_api", __name__)


@ml_api.route("/api/profile/taste", methods=["GET"])
@jwt_required()
def get_taste_profile():
    """Get or generate user's taste profile"""
    user_id = get_jwt_identity()

    # Get existing profile
    profile = (
        TasteProfile.query.join(VolunteerProfile)
        .filter(VolunteerProfile.user_id == user_id)
        .first()
    )

    # Generate if missing or outdated (>7 days)
    if not profile or (datetime.utcnow() - profile.last_updated).days > 7:
        volunteer = VolunteerProfile.query.filter_by(user_id=user_id).first()
        if volunteer:
            generator = TasteProfileGenerator(volunteer.id)
            profile = generator.generate_profile()

    if profile:
        return jsonify({"profile": profile.to_dict()}), 200
    else:
        return jsonify({"error": "Profile not found"}), 404


@ml_api.route("/api/profile/taste/regenerate", methods=["POST"])
@jwt_required()
def regenerate_taste_profile():
    """Force regenerate taste profile"""
    user_id = get_jwt_identity()
    volunteer = VolunteerProfile.query.filter_by(user_id=user_id).first()

    if not volunteer:
        return jsonify({"error": "Volunteer profile not found"}), 404

    generator = TasteProfileGenerator(volunteer.id)
    profile = generator.generate_profile()

    return (
        jsonify({"message": "Profile regenerated", "profile": profile.to_dict()}),
        200,
    )
