from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), unique=False, nullable=False)
    # default active for convenience in tests/dev
    is_active = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    values = db.relationship("UserValues", backref="user", lazy=True)
    achievements = db.relationship("UserAchievement", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

    def __init__(self, **kwargs):
        # Accept `password` as a convenience so tests and callers may pass
        # plain-text passwords. Store only a hashed password in `password_hash`.
        password = kwargs.pop("password", None)
        super().__init__(**kwargs)
        if password:
            self.password_hash = generate_password_hash(password)
            # Store plain password temporarily for test compatibility
            # WARNING: This is only for test purposes and should not be used in production
            self._password = password

    @property
    def password(self):
        """Password property for test compatibility"""
        return getattr(self, "_password", None)

    @password.setter
    def password(self, value):
        """Set password by hashing it"""
        if value:
            self.password_hash = generate_password_hash(value)
            self._password = value

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
        }


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(240), nullable=False)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(240), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(240), nullable=False)
    location = db.Column(db.String(120), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(80), nullable=True)
    image_url = db.Column(db.String(240), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    owner = db.relationship("User")
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organization.id"), nullable=True
    )
    organization = db.relationship("Organization")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "category": self.category,
            "image_url": self.image_url,
            "owner_id": self.owner_id,
            "organization_id": self.organization_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    text = db.Column(db.String(240), nullable=True)  # Optional comment
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User")
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"))
    listing = db.relationship("Listing")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __init__(self, **kwargs):
        # Accept 'comment' as alias for 'text' for backwards compatibility
        if "comment" in kwargs:
            kwargs["text"] = kwargs.pop("comment")
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "comment": self.text,  # Return as 'comment' for API consistency
            "user_id": self.user_id,
            "listing_id": self.listing_id,
        }


class UserValues(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    value = db.Column(db.String(50), nullable=False)


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(240), nullable=False)
    icon = db.Column(db.String(120), nullable=False)  # e.g., a Font Awesome class


class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    achievement_id = db.Column(
        db.Integer, db.ForeignKey("achievement.id"), nullable=False
    )


class SignUp(db.Model):
    """Track volunteer sign-ups for listings."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"), nullable=False)
    message = db.Column(db.String(500), nullable=True)
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # pending, confirmed, cancelled
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    user = db.relationship("User")
    listing = db.relationship("Listing")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "listing_id": self.listing_id,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
