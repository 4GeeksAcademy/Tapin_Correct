from datetime import datetime

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models import (
    db,
    VolunteerProfile,
    Achievement,
    UserAchievement,
    EventRegistration,
    RegistrationStatus,
)


class AchievementChecker:
    """
    Checks and unlocks achievements for volunteers based on their activity.
    """

    def __init__(self, volunteer_id):
        self.volunteer_id = volunteer_id
        self.volunteer = VolunteerProfile.query.get(volunteer_id)

    def check_all_achievements(self):
        """Check all possible achievements for this volunteer"""
        achievements_unlocked = []
        all_achievements = Achievement.query.all()

        for achievement in all_achievements:
            if self._check_achievement_criteria(achievement):
                unlocked = self._unlock_achievement(achievement)
                if unlocked:
                    achievements_unlocked.append(achievement)

        return achievements_unlocked

    def _check_achievement_criteria(self, achievement):
        """Check if volunteer meets achievement criteria"""
        criteria = achievement.criteria or {}

        # Example criteria checks
        if "hours" in criteria:
            if self.volunteer.total_hours_volunteered < criteria["hours"]:
                return False

        if "events" in criteria:
            attended = EventRegistration.query.filter_by(
                volunteer_id=self.volunteer_id, status=RegistrationStatus.ATTENDED
            ).count()
            if attended < criteria["events"]:
                return False

        if "categories" in criteria:
            categories = (
                db.session.query(Achievement)
                .join(EventRegistration)
                .filter(
                    EventRegistration.volunteer_id == self.volunteer_id,
                    EventRegistration.status == RegistrationStatus.ATTENDED,
                )
                .count()
            )
            if categories < criteria["categories"]:
                return False

        return True

    def _unlock_achievement(self, achievement):
        """Unlock achievement if not already unlocked"""
        existing = UserAchievement.query.filter_by(
            volunteer_id=self.volunteer_id, achievement_id=achievement.id
        ).first()

        if existing:
            return None

        user_achievement = UserAchievement(
            volunteer_id=self.volunteer_id,
            achievement_id=achievement.id,
            unlocked_at=datetime.utcnow(),
        )
        db.session.add(user_achievement)
        db.session.commit()

        return user_achievement


# API Endpoint
gamification_api = Blueprint("gamification_api", __name__)


@gamification_api.route("/api/achievements", methods=["GET"])
@jwt_required()
def get_achievements():
    """Get user's achievements"""
    user_id = get_jwt_identity()
    volunteer = VolunteerProfile.query.filter_by(user_id=user_id).first()

    if not volunteer:
        return jsonify({"error": "Volunteer profile not found"}), 404

    unlocked = (
        db.session.query(Achievement)
        .join(UserAchievement)
        .filter(UserAchievement.volunteer_id == volunteer.id)
        .all()
    )

    all_achievements = Achievement.query.all()

    return (
        jsonify(
            {
                "unlocked_count": len(unlocked),
                "total_count": len(all_achievements),
                "unlocked": [a.to_dict() for a in unlocked],
                "locked": [a.to_dict() for a in all_achievements if a not in unlocked],
            }
        ),
        200,
    )


@gamification_api.route("/api/achievements/check", methods=["POST"])
@jwt_required()
def check_achievements():
    """Manually trigger achievement check"""
    user_id = get_jwt_identity()
    volunteer = VolunteerProfile.query.filter_by(user_id=user_id).first()

    if not volunteer:
        return jsonify({"error": "Volunteer profile not found"}), 404

    checker = AchievementChecker(volunteer.id)
    new_achievements = checker.check_all_achievements()

    return (
        jsonify(
            {
                "new_achievements": len(new_achievements),
                "achievements": [a.to_dict() for a in new_achievements],
            }
        ),
        200,
    )
