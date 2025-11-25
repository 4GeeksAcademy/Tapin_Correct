from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="volunteer")
    organization_name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "user_type": self.role,
            "organization_name": self.organization_name,
        }


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    values = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        values_list = []
        if self.values:
            try:
                values_list = json.loads(self.values)
            except:
                values_list = []

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "category": self.category,
            "values": values_list,
            "image_url": self.image_url,
            "owner_id": self.owner_id,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
        }


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class SignUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"), nullable=False)
    status = db.Column(db.String(50), default="pending")
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint("user_id", "listing_id", name="_user_listing_uc"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "listing_id": self.listing_id,
            "status": self.status,
            "message": self.message,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
        }


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint("user_id", "listing_id", name="_user_listing_review_uc"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "listing_id": self.listing_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
        }


class Event(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.Text, nullable=False)
    organization = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_start = db.Column(db.DateTime, nullable=True)
    location_address = db.Column(db.Text)
    location_city = db.Column(db.String(120))
    location_state = db.Column(db.String(10))
    location_zip = db.Column(db.String(20))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    geohash_4 = db.Column(db.String(8))
    geohash_6 = db.Column(db.String(12), index=True)
    category = db.Column(db.String(100))
    values = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(1000), unique=False)
    source = db.Column(db.String(200))
    venue = db.Column(db.String(200), nullable=True)
    price = db.Column(db.String(100), nullable=True)
    contact_email = db.Column(db.String(200), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    contact_person = db.Column(db.String(200), nullable=True)
    scraped_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    cache_expires_at = db.Column(db.DateTime, nullable=True, index=True)
    image_url = db.Column(db.String(1000), nullable=True)
    image_urls = db.Column(db.Text, nullable=True)

    def to_dict(self):
        images_list = []
        if hasattr(self, "images") and self.images:
            images_list = [
                {"url": img.url, "caption": img.caption, "position": img.position}
                for img in sorted(self.images, key=lambda x: x.position)
            ]
        values_list = []
        if self.values:
            try:
                values_list = json.loads(self.values)
            except:
                values_list = []

        return {
            "id": self.id,
            "title": self.title,
            "organization": self.organization,
            "description": self.description,
            "date_start": (self.date_start.isoformat() if self.date_start else None),
            "location_address": self.location_address,
            "city": self.location_city,
            "state": self.location_state,
            "zip": self.location_zip,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "category": self.category,
            "values": values_list,
            "url": self.url,
            "source": self.source,
            "venue": self.venue,
            "price": self.price,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "contact_person": self.contact_person,
            "scraped_at": (self.scraped_at.isoformat() if self.scraped_at else None),
            "image_url": self.image_url,
            "image_urls": self.image_urls,
            "images": images_list,
        }


class EventImage(db.Model):
    __tablename__ = "event_image"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.String(36), db.ForeignKey("event.id"), nullable=False, index=True
    )
    url = db.Column(db.String(1000), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "url": self.url,
            "caption": self.caption,
            "position": self.position,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
        }


Event.images = db.relationship(
    "EventImage", backref="event", cascade="all, delete-orphan", lazy="dynamic"
)


class UserEventInteraction(db.Model):
    __tablename__ = "user_event_interaction"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    event_id = db.Column(
        db.String(36), db.ForeignKey("event.id"), nullable=False, index=True
    )
    interaction_type = db.Column(db.String(20), nullable=False)
    interaction_metadata = db.Column(db.Text, nullable=True)
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    event = db.relationship("Event", backref="interactions", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "interaction_type": self.interaction_type,
            "metadata": self.interaction_metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class UserAchievement(db.Model):
    __tablename__ = "user_achievement"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    achievement_type = db.Column(db.String(50), nullable=False)
    progress = db.Column(db.Integer, default=0)
    unlocked = db.Column(db.Boolean, default=False, index=True)
    unlocked_at = db.Column(db.DateTime, nullable=True)
    achievement_metadata = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "achievement_type": self.achievement_type,
            "progress": self.progress,
            "unlocked": self.unlocked,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "metadata": self.achievement_metadata,
        }


class UserProfile(db.Model):
    __tablename__ = "user_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True, index=True
    )
    taste_profile = db.Column(db.Text, nullable=True)
    adventure_level = db.Column(db.Float, default=0.5)
    price_sensitivity = db.Column(db.String(20), default="medium")
    favorite_venues = db.Column(db.Text, nullable=True)
    notification_preferences = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "taste_profile": self.taste_profile,
            "adventure_level": self.adventure_level,
            "price_sensitivity": self.price_sensitivity,
            "favorite_venues": self.favorite_venues,
            "notification_preferences": self.notification_preferences,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
