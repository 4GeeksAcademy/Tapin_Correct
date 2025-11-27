from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import (
    db,
    User,
    VolunteerProfile,
    OrganizationProfile,
    UserType,
    VerificationStatus,
)

profile_bp = Blueprint("profile", __name__)


# ═══════════════════════════════════════════════════════════════
# GENERIC PROFILE ENDPOINTS
# ═══════════════════════════════════════════════════════════════


@profile_bp.route("/api/me", methods=["GET"])
@jwt_required()
def get_current_user_profile():
    """Get current logged-in user's profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    profile_data = {}

    if user.user_type == UserType.VOLUNTEER:
        profile = VolunteerProfile.query.filter_by(user_id=user.id).first()
        if profile:
            profile_data = profile.to_dict()

    elif user.user_type == UserType.ORGANIZATION:
        profile = OrganizationProfile.query.filter_by(user_id=user.id).first()
        if profile:
            profile_data = profile.to_dict()

    return (
        jsonify(
            {
                "user": {
                    "email": user.email,
                    "user_type": user.user_type.value,
                    "id": user.id,
                },
                "profile": profile_data,
            }
        ),
        200,
    )


# ═══════════════════════════════════════════════════════════════
# VOLUNTEER PROFILE ENDPOINTS
# ═══════════════════════════════════════════════════════════════


@profile_bp.route("/api/profile/volunteer", methods=["PUT"])
@jwt_required()
def update_volunteer_profile():
    """Create or update volunteer profile"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    profile = VolunteerProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        profile = VolunteerProfile(user_id=user_id)
        db.session.add(profile)

    # Update fields safely
    fields = [
        "first_name",
        "last_name",
        "bio",
        "city",
        "state",
        "skills",
        "interests",
        "avatar_url",
        "phone_number",
    ]

    for field in fields:
        if field in data:
            setattr(profile, field, data[field])

    db.session.commit()

    return (
        jsonify(
            {"message": "Profile updated successfully", "profile": profile.to_dict()}
        ),
        200,
    )


# ═══════════════════════════════════════════════════════════════
# ORGANIZATION PROFILE ENDPOINTS
# ═══════════════════════════════════════════════════════════════


@profile_bp.route("/api/profile/organization", methods=["PUT"])
@jwt_required()
def update_org_profile():
    """Create or update organization profile"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    profile = OrganizationProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        profile = OrganizationProfile(user_id=user_id)
        db.session.add(profile)

    # Update fields
    fields = [
        "organization_name",
        "description",
        "website",
        "city",
        "state",
        "logo_url",
        "contact_email",
        "organization_type",
    ]

    for field in fields:
        if field in data:
            setattr(profile, field, data[field])

    # Handle verification docs separately if needed
    if "verification_documents" in data:
        profile.verification_documents = data["verification_documents"]
        # Trigger admin review status reset if docs change
        # profile.verification_status = VerificationStatus.PENDING

    db.session.commit()

    return (
        jsonify(
            {"message": "Organization profile updated", "profile": profile.to_dict()}
        ),
        200,
    )


@profile_bp.route("/api/organizations/<int:org_id>", methods=["GET"])
def get_public_org_profile(org_id):
    """Get public organization profile (no auth required)"""
    org = OrganizationProfile.query.get_or_404(org_id)

    return (
        jsonify(
            {
                "organization": org.to_dict(),
                "events_count": len(getattr(org, "events", [])),
            }
        ),
        200,
    )


@profile_bp.route("/api/organizations/unclaimed", methods=["GET"])
def list_unclaimed_organizations():
    """Return a list of organization profiles that are unclaimed."""
    # Prefer explicit UNCLAIMED status if present, otherwise fallback to user_id is NULL
    try:
        orgs = OrganizationProfile.query.filter(
            (OrganizationProfile.verification_status == VerificationStatus.UNCLAIMED)
            | (OrganizationProfile.user_id == None)
        ).all()
    except Exception:
        orgs = OrganizationProfile.query.filter(
            OrganizationProfile.user_id == None
        ).all()

    return jsonify({"organizations": [o.to_dict() for o in orgs]}), 200


@profile_bp.route("/api/organizations/<int:org_id>/claim", methods=["POST"])
@jwt_required()
def claim_organization(org_id):
    """Authenticated user requests to claim an unclaimed organization profile."""
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass

    org = OrganizationProfile.query.get_or_404(org_id)

    # Only allow claiming if the org is currently unclaimed
    if org.user_id:
        return jsonify({"error": "organization already claimed"}), 400

    data = request.get_json() or {}
    org.claiming_user_id = user_id
    if "verification_documents" in data:
        org.verification_documents = data["verification_documents"]

    # Move to pending review
    org.verification_status = VerificationStatus.PENDING
    db.session.commit()

    return jsonify({"message": "claim submitted", "organization": org.to_dict()}), 200
