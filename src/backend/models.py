from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()


# Enums
class UserType(enum.Enum):
    VOLUNTEER = "volunteer"
    ORGANIZATION = "organization"
    ADMIN = "admin"


class VerificationStatus(enum.Enum):
    UNCLAIMED = "unclaimed"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class EventStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class InteractionType(enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    VIEW = "view"
    SHARE = "share"
    REGISTER = "register"


class RegistrationStatus(enum.Enum):
    REGISTERED = "registered"
    WAITLIST = "waitlist"
    CONFIRMED = "confirmed"
    ATTENDED = "attended"
    CANCELLED = "cancelled"


# ═══════════════════════════════════════════════════════════════
# CORE USER MODELS
# ═══════════════════════════════════════════════════════════════


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum(UserType), nullable=False, default=UserType.VOLUNTEER)
    email_verified = db.Column(db.Boolean, default=False)
    profile_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    volunteer_profile = db.relationship(
        "VolunteerProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="[VolunteerProfile.user_id]",
    )
    organization_profile = db.relationship(
        "OrganizationProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="[OrganizationProfile.user_id]",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "user_type": self.user_type.value,
            "profile_completed": self.profile_completed,
        }


class VolunteerProfile(db.Model):
    __tablename__ = "volunteer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    # `user_id` may be NULL for unclaimed organization profiles
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True, unique=True
    )

    # If a logged-in user has started a claim flow, store who is claiming
    claiming_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Basic Info
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    date_of_birth = db.Column(db.Date)
    phone_number = db.Column(db.String(20))

    # Location
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))

    # Preferences (stored as JSON)
    skills = db.Column(db.JSON, default=list)
    interests = db.Column(db.JSON, default=list)
    availability = db.Column(db.JSON, default=dict)

    # Stats
    total_hours_volunteered = db.Column(db.Integer, default=0)
    events_attended = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "city": self.city,
            "skills": self.skills,
            "interests": self.interests,
            "total_hours_volunteered": self.total_hours_volunteered,
        }


class OrganizationProfile(db.Model):
    __tablename__ = "organization_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )

    # Basic Info
    organization_name = db.Column(db.String(200), nullable=False)
    organization_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    website = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))

    # Location
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))

    # Verification
    verification_status = db.Column(
        db.Enum(VerificationStatus), default=VerificationStatus.PENDING
    )
    verification_documents = db.Column(db.JSON, default=dict)
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.Integer)

    total_events = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "organization_name": self.organization_name,
            "description": self.description,
            "logo_url": self.logo_url,
            "city": self.city,
            "verification_status": (
                self.verification_status.value if self.verification_status else None
            ),
            "verified": self.verification_status == VerificationStatus.VERIFIED,
            "claiming_user_id": self.claiming_user_id,
            "is_claimed": bool(self.user_id),
        }


# ═══════════════════════════════════════════════════════════════
# EVENT MODELS
# ═══════════════════════════════════════════════════════════════


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organization_profiles.id"), nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))

    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    location_name = db.Column(db.String(200))
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    max_volunteers = db.Column(db.Integer)
    current_volunteers = db.Column(db.Integer, default=0)

    image_url = db.Column(db.String(500))
    status = db.Column(db.Enum(EventStatus), default=EventStatus.DRAFT)
    source = db.Column(db.String(20), default="internal")
    external_url = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # registrations = db.relationship('EventRegistration', backref='event', cascade='all, delete-orphan')


class UserEventInteraction(db.Model):
    __tablename__ = "user_event_interactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    event_id = db.Column(db.String(100))
    event_title = db.Column(db.String(200))
    category = db.Column(db.String(50))
    interaction_type = db.Column(db.Enum(InteractionType), nullable=False)
    source = db.Column(db.String(20))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class EventRegistration(db.Model):
    __tablename__ = "event_registrations"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    volunteer_id = db.Column(
        db.Integer, db.ForeignKey("volunteer_profiles.id"), nullable=False
    )

    status = db.Column(
        db.Enum(RegistrationStatus), default=RegistrationStatus.REGISTERED
    )
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
