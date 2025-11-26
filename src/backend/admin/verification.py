from functools import wraps
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models import (
    db,
    User,
    OrganizationProfile,
    UserType,
    VerificationStatus,
)


admin_api = Blueprint("admin_api", __name__)


def require_admin(func):
    """Decorator to require admin user type"""

    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or getattr(user, "user_type", None) != UserType.ADMIN:
            return jsonify({"error": "Admin access required"}), 403
        return func(*args, **kwargs)

    return wrapper


@admin_api.route("/api/admin/organizations/pending", methods=["GET"])
@require_admin
def get_pending_verifications():
    """Get all organizations pending verification"""
    pending = (
        OrganizationProfile.query.filter_by(
            verification_status=VerificationStatus.PENDING
        )
        .order_by(OrganizationProfile.created_at.desc())
        .all()
    )

    return (
        jsonify(
            {"count": len(pending), "organizations": [org.to_dict() for org in pending]}
        ),
        200,
    )


@admin_api.route("/api/admin/organizations/<int:org_id>", methods=["GET"])
@require_admin
def get_organization_details(org_id):
    """Get full organization details for verification"""
    org = OrganizationProfile.query.get_or_404(org_id)
    user = User.query.get(org.user_id)

    return (
        jsonify(
            {
                "organization": org.to_dict(),
                "user_email": getattr(user, "email", None),
                "user_created": (
                    getattr(user, "created_at", None).isoformat()
                    if getattr(user, "created_at", None)
                    else None
                ),
                "documents": org.verification_documents,
                "events_created": org.total_events,
            }
        ),
        200,
    )


@admin_api.route("/api/admin/organizations/<int:org_id>/verify", methods=["PUT"])
@require_admin
def verify_organization(org_id):
    """Approve or reject organization verification"""
    data = request.get_json() or {}
    action = data.get("action")  # 'approve' or 'reject'
    notes = data.get("notes", "")

    if action not in ["approve", "reject"]:
        return jsonify({"error": "Invalid action"}), 400

    org = OrganizationProfile.query.get_or_404(org_id)
    admin_user_id = get_jwt_identity()

    if action == "approve":
        org.verification_status = VerificationStatus.VERIFIED
        org.verified_at = datetime.utcnow()
        org.verified_by = admin_user_id

        # send_verification_email(org.user_id, approved=True)  # implement separately

        db.session.commit()
        return (
            jsonify(
                {"message": "Organization verified", "organization": org.to_dict()}
            ),
            200,
        )

    else:  # reject
        org.verification_status = VerificationStatus.REJECTED
        if not org.verification_documents:
            org.verification_documents = {}
        org.verification_documents["rejection_reason"] = notes
        org.verification_documents["rejected_by"] = admin_user_id
        org.verification_documents["rejected_at"] = datetime.utcnow().isoformat()

        # send_verification_email(org.user_id, approved=False, reason=notes)

        db.session.commit()
        return (
            jsonify({"message": "Organization verification rejected", "reason": notes}),
            200,
        )


@admin_api.route("/api/admin/statistics", methods=["GET"])
@require_admin
def get_platform_statistics():
    """Get platform-wide statistics"""
    from sqlalchemy import func
    from backend.models import Event, EventRegistration, RegistrationStatus

    stats = {
        "users": {
            "total": User.query.count(),
            "volunteers": User.query.filter_by(user_type=UserType.VOLUNTEER).count(),
            "organizations": User.query.filter_by(
                user_type=UserType.ORGANIZATION
            ).count(),
            "verified_orgs": OrganizationProfile.query.filter_by(
                verification_status=VerificationStatus.VERIFIED
            ).count(),
        },
        "events": {
            "total": Event.query.count(),
            "published": (
                Event.query.filter_by(
                    status=(
                        Event.status.property.columns[0].type.enums[0]
                        if hasattr(Event, "status")
                        else None
                    )
                ).count()
                if hasattr(Event, "status")
                else Event.query.count()
            ),
            "completed": (
                Event.query.filter_by(
                    status=(
                        Event.status.property.columns[0].type.enums[0]
                        if hasattr(Event, "status")
                        else None
                    )
                ).count()
                if hasattr(Event, "status")
                else 0
            ),
        },
        "engagement": {
            "total_interactions": UserEventInteraction.query.count(),
            "total_registrations": (
                EventRegistration.query.count()
                if "EventRegistration" in globals()
                else 0
            ),
            "attended": (
                EventRegistration.query.filter_by(
                    status=RegistrationStatus.ATTENDED
                ).count()
                if "EventRegistration" in globals()
                else 0
            ),
        },
        "pending_verifications": OrganizationProfile.query.filter_by(
            verification_status=VerificationStatus.PENDING
        ).count(),
    }

    return jsonify(stats), 200


@admin_api.route("/api/admin/users/<int:user_id>/suspend", methods=["PUT"])
@require_admin
def suspend_user(user_id):
    """Suspend a user account"""
    data = request.get_json() or {}
    reason = data.get("reason", "No reason provided")

    user = User.query.get_or_404(user_id)

    # You may want to add suspension fields to the User model; here we only commit a placeholder
    # user.suspended = True
    # user.suspension_reason = reason

    db.session.commit()

    return (
        jsonify({"message": "User suspended", "user_id": user_id, "reason": reason}),
        200,
    )
