from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from auth import token_for
from flask_cors import CORS
from datetime import datetime, timezone
import os
import json
import logging
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import smtplib
from email.message import EmailMessage
from google_search import (
    search_events,
    create_events_from_search_results,
    enrich_events_with_contact_info,
    enrich_events_with_values,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
# Load .env from repository root in development if python-dotenv is installed
try:
    from dotenv import load_dotenv

    repo_root = os.path.abspath(os.path.join(base_dir, ".."))
    env_candidates = [
        os.path.join(repo_root, ".env"),
        os.path.join(repo_root, "..", ".env"),
    ]
    for env_path in env_candidates:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            break
except Exception:
    # python-dotenv not installed or .env missing; proceed with environment
    # variables
    pass

# Allow overriding the database URL via environment (useful for CI or
# production)
default_db = "sqlite:///" + os.path.join(base_dir, "data.db")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", default_db
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Supabase connection pooling configuration for transaction mode (port 6543)
# Configure SQLAlchemy engine options; adapt connect_args by driver
db_url = app.config["SQLALCHEMY_DATABASE_URI"]
engine_options = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": 5,
    "max_overflow": 10,
}

# Use PostgreSQL-specific connect args only when using psycopg2
if isinstance(db_url, str) and db_url.lower().startswith("postgresql"):
    engine_options["connect_args"] = {
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000",
    }
elif isinstance(db_url, str) and db_url.lower().startswith("sqlite"):
    # SQLite does not accept the above options; leave empty or set
    # sqlite-specific options
    engine_options["connect_args"] = {}

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options
# Secret key used for serializer tokens and other Flask features
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", app.config["SECRET_KEY"]
)
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
    "SECURITY_PASSWORD_SALT", "dev-salt"
)

CORS(app)

# Register blueprints
try:
    from backend.routes.events import events_bp
except ModuleNotFoundError:
    from routes.events import events_bp

app.register_blueprint(events_bp, url_prefix="/events")

db = SQLAlchemy(app)
jwt = JWTManager(app)


def _warn_on_default_secrets():
    """Log warning if secret env vars are left at their dev defaults.

    This is only advisory and will not stop the app from running. It's helpful
    for local dev and in CI to call out missing secret configuration.
    """
    defaults = {
        "SECRET_KEY": "dev-secret-key",
        "SECURITY_PASSWORD_SALT": "dev-salt",
    }
    missing = []
    for key, default_val in defaults.items():
        val = os.environ.get(key, app.config.get(key))
        if not val or (isinstance(val, str) and val == default_val):
            missing.append(key)
    # JWT_SECRET_KEY may default to SECRET_KEY; still warn if it's the same as
    # the dev key
    jwt_key = os.environ.get("JWT_SECRET_KEY", app.config.get("JWT_SECRET_KEY"))
    if not jwt_key or (
        jwt_key == app.config.get("SECRET_KEY") == defaults["SECRET_KEY"]
    ):
        missing.append("JWT_SECRET_KEY")

    if missing:
        app.logger.warning(
            "Missing or default secrets detected: %s.\n"
            "For local dev copy `.env.sample` -> `.env` and set strong values."
            " See backend/CONFIG.md for details.",
            ", ".join(sorted(set(missing))),
        )


_warn_on_default_secrets()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Role: 'volunteer', 'organization', or 'user' (default)
    role = db.Column(db.String(50), default="volunteer")
    # Organization name (only for role='organization')
    organization_name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "user_type": self.role,  # Alias for clarity (volunteer/organization)
            "organization_name": self.organization_name,
        }


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    # Community, Environment, Education, Health, Animals
    category = db.Column(db.String(100), nullable=True)
    # Organization values (JSON array of value strings)
    values = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json

        # Parse values JSON if present
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
    """Simple persistent items for the MVP /api/items endpoints."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class SignUp(db.Model):
    """Track volunteer sign-ups for listings."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"), nullable=False)
    # pending, accepted, declined, cancelled
    status = db.Column(db.String(50), default="pending")
    message = db.Column(db.Text)  # Optional message from volunteer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Add unique constraint to prevent duplicate sign-ups
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
    """User reviews for listings."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Add unique constraint to prevent multiple reviews from same user
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
    """Cached scraped volunteer events for geohash-based lookup."""

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
    # Event/organization values (JSON array of value strings)
    values = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(1000), unique=False)
    source = db.Column(db.String(200))
    venue = db.Column(db.String(200), nullable=True)  # Event venue name
    price = db.Column(db.String(100), nullable=True)  # Event price/cost
    # Contact information for volunteer events
    contact_email = db.Column(db.String(200), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    contact_person = db.Column(db.String(200), nullable=True)
    scraped_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    cache_expires_at = db.Column(db.DateTime, nullable=True, index=True)
    # Optional image link (single) and multiple image links (JSON text)
    image_url = db.Column(db.String(1000), nullable=True)
    image_urls = db.Column(db.Text, nullable=True)

    def to_dict(self):
        import json

        # Include normalized images if available
        images_list = []
        if hasattr(self, "images") and self.images:
            images_list = [
                {"url": img.url, "caption": img.caption, "position": img.position}
                for img in sorted(self.images, key=lambda x: x.position)
            ]

        # Parse values JSON if present
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
    """Normalized event images table. One row per image per event."""

    __tablename__ = "event_image"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.String(36), db.ForeignKey("event.id"), nullable=False, index=True
    )
    url = db.Column(db.String(1000), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, nullable=True)  # ordering of images
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


# Add relationship on Event to access images
Event.images = db.relationship(
    "EventImage", backref="event", cascade="all, delete-orphan", lazy="dynamic"
)


class UserEventInteraction(db.Model):
    """Track user interactions with events for personalization."""

    __tablename__ = "user_event_interaction"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    event_id = db.Column(
        db.String(36), db.ForeignKey("event.id"), nullable=False, index=True
    )
    interaction_type = db.Column(
        db.String(20), nullable=False
    )  # view, like, dislike, attend, skip, super_like
    interaction_metadata = db.Column(
        db.Text, nullable=True
    )  # JSON with additional data (time_spent, swipe_direction, etc.)
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    # Relationships
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
    """Track user achievements and badges for gamification."""

    __tablename__ = "user_achievement"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    achievement_type = db.Column(
        db.String(50), nullable=False
    )  # weekend_warrior, category_completionist, etc.
    progress = db.Column(db.Integer, default=0)  # Progress towards achievement
    unlocked = db.Column(db.Boolean, default=False, index=True)
    unlocked_at = db.Column(db.DateTime, nullable=True)
    achievement_metadata = db.Column(
        db.Text, nullable=True
    )  # JSON with additional data

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
    """Extended user profile for personalization."""

    __tablename__ = "user_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True, index=True
    )
    taste_profile = db.Column(
        db.Text, nullable=True
    )  # JSON with category preferences, etc.
    adventure_level = db.Column(db.Float, default=0.5)  # 0-1 scale
    price_sensitivity = db.Column(db.String(20), default="medium")  # low, medium, high
    favorite_venues = db.Column(db.Text, nullable=True)  # JSON array
    notification_preferences = db.Column(db.Text, nullable=True)  # JSON
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


def get_serializer():
    return URLSafeTimedSerializer(app.config["SECRET_KEY"])


# Ensure database tables exist when the app starts. Using app.app_context()
# is more robust than the before_first_request decorator which may not be
# available in all runtime contexts.
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return jsonify({"message": "Tapin Backend API Root"})


@app.route("/api/health", methods=["GET"])
def api_health():
    """Enhanced health check including database connectivity."""
    health_status = {"status": "ok", "components": {}}

    # Check database connection
    try:
        db.session.execute(db.text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "connected",
            "uri_prefix": app.config["SQLALCHEMY_DATABASE_URI"][:20] + "...",
            "pool_size": (
                db.engine.pool.size() if hasattr(db.engine.pool, "size") else "N/A"
            ),
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["database"] = {"status": "error", "error": str(e)}
        return jsonify(health_status), 503

    return jsonify(health_status), 200


@app.route("/api/items", methods=["GET"])
def api_list_items():
    # Return all items from the database
    items = Item.query.order_by(Item.id.asc()).all()
    return jsonify({"items": [i.to_dict() for i in items]}), 200


@app.route("/api/items", methods=["POST"])
@jwt_required()
def api_create_item():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name required"}), 400
    item = Item(name=name, description=data.get("description"))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user_type = data.get("user_type", "volunteer")  # 'volunteer' or 'organization'
    organization_name = data.get("organization_name")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    # Validate user_type
    if user_type not in ["volunteer", "organization"]:
        return (
            jsonify({"error": "user_type must be 'volunteer' or 'organization'"}),
            400,
        )

    # Validate organization name if user_type is organization
    if user_type == "organization" and not organization_name:
        return jsonify({"error": "organization name required for organizations"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "user already exists"}), 400

    pw_hash = generate_password_hash(password)
    user = User(
        email=email,
        password_hash=pw_hash,
        role=user_type,
        organization_name=organization_name if user_type == "organization" else None,
    )
    db.session.add(user)
    db.session.commit()

    # return both access and refresh tokens (identity stored as string)
    from auth import token_pair

    tokens = token_pair(user)
    return (
        jsonify(
            {
                "message": f"{user_type} account created successfully",
                "user": user.to_dict(),
                **tokens,
            }
        ),
        201,
    )


@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401
    # return both access and refresh tokens to the client
    from auth import token_pair

    tokens = token_pair(user)
    return jsonify({"message": "login successful", "user": user.to_dict(), **tokens})


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    """Exchange a valid refresh token for a new access token."""
    uid = get_jwt_identity()
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid
    user = db.session.get(User, uid_int)
    if not user:
        return jsonify({"error": "user not found"}), 404
    access_token = token_for(uid_int)
    return jsonify({"access_token": access_token})


@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    uid = get_jwt_identity()
    # convert back to int because tokens store identity as string
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid
    # Use Session.get() which is the modern SQLAlchemy API (avoids
    # LegacyAPIWarning)
    user = db.session.get(User, uid_int)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"user": user.to_dict()})


def send_reset_email(to_email, reset_url):
    smtp_host = os.environ.get("SMTP_HOST")
    if not smtp_host:
        return False, "SMTP not configured"
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")

    msg = EmailMessage()
    msg["Subject"] = "Tapin Password Reset"
    msg["From"] = smtp_user or f"no-reply@{smtp_host}"
    msg["To"] = to_email
    msg.set_content(f"Use the link to reset your password: {reset_url}")

    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True, "sent"
    except Exception as e:
        return False, str(e)


@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "email required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        # Do not reveal whether the email exists
        msg = "If an account exists for that email, a reset link was sent."
        return jsonify({"message": msg})

    serializer = get_serializer()
    token = serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])
    reset_url = url_for("confirm_reset", token=token, _external=True)

    sent, info = send_reset_email(email, reset_url)
    if sent:
        return jsonify({"message": "reset email sent"})
    else:
        # Fallback in dev: return the reset_url so developers can use it
        return jsonify(
            {
                "message": "smtp not configured, returning reset link (dev)",
                "reset_url": reset_url,
                "error": info,
            }
        )


@app.route("/reset-password/confirm/<token>", methods=["POST"])
def confirm_reset(token):
    data = request.get_json() or {}
    new_password = data.get("password")
    if not new_password:
        return jsonify({"error": "password required"}), 400
    serializer = get_serializer()
    try:
        email = serializer.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=3600
        )
    except SignatureExpired:
        return jsonify({"error": "token expired"}), 400
    except BadSignature:
        return jsonify({"error": "invalid token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "no such user"}), 404
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"message": "password updated"})


@app.route("/listings", methods=["GET"])
def get_listings():
    # Support simple filtering via query params: q (text search on
    # title/description or category), location
    q = request.args.get("q", type=str)
    location = request.args.get("location", type=str)

    query = Listing.query
    if q:
        # Check if q matches a category exactly (case-insensitive)
        categories = ["Community", "Environment", "Education", "Health", "Animals"]
        if q.lower() in [c.lower() for c in categories]:
            # Filter by category
            query = query.filter(Listing.category.ilike(q))
        else:
            # Text search on title/description
            like = f"%{q}%"
            query = query.filter(
                (Listing.title.ilike(like)) | (Listing.description.ilike(like))
            )
    if location:
        query = query.filter(Listing.location.ilike(f"%{location}%"))

    listings = query.order_by(Listing.created_at.desc()).all()
    return jsonify([lst.to_dict() for lst in listings])


@app.route("/listings", methods=["POST"])
@jwt_required()
def create_listing():
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title required"}), 400
    # JWT identity is stored as string; convert back to int for DB foreign key
    owner_id = int(get_jwt_identity())
    # Validate optional category
    category = data.get("category")
    allowed = ["Community", "Environment", "Education", "Health", "Animals"]
    if category and category not in allowed:
        return jsonify({"error": "invalid category"}), 400

    # Parse optional coordinates
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    try:
        latitude = float(latitude) if latitude is not None else None
        longitude = float(longitude) if longitude is not None else None
    except (TypeError, ValueError):
        return jsonify({"error": "invalid coordinates"}), 400

    listing = Listing(
        title=title,
        description=data.get("description"),
        location=data.get("location"),
        latitude=latitude,
        longitude=longitude,
        category=category,
        image_url=data.get("image_url"),
        owner_id=owner_id,
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify(listing.to_dict()), 201


@app.route("/listings/<int:id>", methods=["GET"])
def get_listing_detail(id):
    listing = Listing.query.get_or_404(id)
    return jsonify(listing.to_dict())


@app.route("/listings/<int:id>", methods=["PUT"])
@jwt_required()
def update_listing(id):
    listing = Listing.query.get_or_404(id)
    # Verify ownership
    owner_id = int(get_jwt_identity())
    if listing.owner_id != owner_id:
        return jsonify({"error": "unauthorized - you don't own this listing"}), 403
    data = request.get_json() or {}
    listing.title = data.get("title", listing.title)
    listing.description = data.get("description", listing.description)
    listing.location = data.get("location", listing.location)
    # Optional fields
    if "category" in data:
        category = data.get("category")
        allowed = ["Community", "Environment", "Education", "Health", "Animals"]
        if category and category not in allowed:
            return jsonify({"error": "invalid category"}), 400
        listing.category = category
    if "image_url" in data:
        listing.image_url = data.get("image_url")
    if "latitude" in data or "longitude" in data:
        try:
            if "latitude" in data:
                listing.latitude = (
                    float(data.get("latitude"))
                    if data.get("latitude") is not None
                    else None
                )
            if "longitude" in data:
                listing.longitude = (
                    float(data.get("longitude"))
                    if data.get("longitude") is not None
                    else None
                )
        except (TypeError, ValueError):
            return jsonify({"error": "invalid coordinates"}), 400
    db.session.commit()
    return jsonify(listing.to_dict())


@app.route("/listings/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_listing(id):
    listing = Listing.query.get_or_404(id)
    # Verify ownership
    owner_id = int(get_jwt_identity())
    if listing.owner_id != owner_id:
        return jsonify({"error": "unauthorized - you don't own this listing"}), 403
    db.session.delete(listing)
    db.session.commit()
    return jsonify({"message": "deleted"})


@app.route("/listings/<int:id>/signup", methods=["POST"])
@jwt_required()
def signup_for_listing(id):
    """Volunteer signs up for a listing."""
    _listing = Listing.query.get_or_404(id)  # noqa: F841 validate exists
    user_id = int(get_jwt_identity())

    # Check if already signed up
    existing = SignUp.query.filter_by(user_id=user_id, listing_id=id).first()
    if existing:
        return jsonify({"error": "already signed up for this listing"}), 400

    data = request.get_json() or {}
    signup = SignUp(
        user_id=user_id, listing_id=id, message=data.get("message"), status="pending"
    )
    db.session.add(signup)
    db.session.commit()

    return jsonify(signup.to_dict()), 201


@app.route("/listings/<int:id>/signups", methods=["GET"])
@jwt_required()
def get_listing_signups(id):
    """Get all sign-ups for a listing (owner only)."""
    listing = Listing.query.get_or_404(id)
    owner_id = int(get_jwt_identity())

    # Verify ownership
    if listing.owner_id != owner_id:
        return jsonify({"error": "unauthorized - you don't own this listing"}), 403

    signups = (
        SignUp.query.filter_by(listing_id=id).order_by(SignUp.created_at.desc()).all()
    )

    # Include user email with each sign-up
    results = []
    for signup in signups:
        signup_dict = signup.to_dict()
        user = db.session.get(User, signup.user_id)
        if user:
            signup_dict["user_email"] = user.email
        results.append(signup_dict)

    return jsonify(results)


@app.route("/signups/<int:id>", methods=["PUT"])
@jwt_required()
def update_signup_status(id):
    """Update sign-up status (owner accept/decline, volunteer cancel)."""
    signup = SignUp.query.get_or_404(id)
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "status required"}), 400

    # Get the listing to check ownership
    listing = db.session.get(Listing, signup.listing_id)
    if not listing:
        return jsonify({"error": "listing not found"}), 404

    # Owner can accept/decline, volunteer can cancel
    if listing.owner_id == user_id:
        if new_status not in ["accepted", "declined"]:
            err = "owner can only set status to accepted or declined"
            return jsonify({"error": err}), 400
    elif signup.user_id == user_id:
        if new_status != "cancelled":
            return jsonify({"error": "volunteer can only cancel sign-up"}), 400
    else:
        return jsonify({"error": "unauthorized"}), 403

    signup.status = new_status
    db.session.commit()
    return jsonify(signup.to_dict())


@app.route("/listings/<int:id>/reviews", methods=["POST"])
@jwt_required()
def create_review(id):
    """Create a review for a listing."""
    _listing = Listing.query.get_or_404(id)  # noqa: F841 validate exists
    user_id = int(get_jwt_identity())

    # Check if already reviewed
    existing = Review.query.filter_by(user_id=user_id, listing_id=id).first()
    if existing:
        return jsonify({"error": "you have already reviewed this listing"}), 400

    data = request.get_json() or {}
    rating = data.get("rating")

    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        err = "rating must be an integer between 1 and 5"
        return jsonify({"error": err}), 400

    review = Review(
        user_id=user_id, listing_id=id, rating=rating, comment=data.get("comment")
    )
    db.session.add(review)
    db.session.commit()

    return jsonify(review.to_dict()), 201


@app.route("/listings/<int:id>/reviews", methods=["GET"])
def get_listing_reviews(id):
    """Get all reviews for a listing."""
    _listing = Listing.query.get_or_404(id)  # noqa: F841 validate exists
    reviews = (
        Review.query.filter_by(listing_id=id).order_by(Review.created_at.desc()).all()
    )

    # Include user email with each review
    results = []
    for review in reviews:
        review_dict = review.to_dict()
        user = db.session.get(User, review.user_id)
        if user:
            review_dict["user_email"] = user.email
        results.append(review_dict)

    return jsonify(results)


@app.route("/listings/<int:id>/average-rating", methods=["GET"])
def get_listing_average_rating(id):
    """Get average rating for a listing."""
    _listing = Listing.query.get_or_404(id)  # noqa: F841 validate exists
    reviews = Review.query.filter_by(listing_id=id).all()

    if not reviews:
        return jsonify({"average_rating": 0, "review_count": 0})

    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    return jsonify(
        {"average_rating": round(avg_rating, 1), "review_count": len(reviews)}
    )


@app.route("/api/discover-events", methods=["POST"])
@jwt_required()
def discover_events():
    """Discover volunteer opportunities using hybrid LLM and web scraping.

    Searches for volunteer events by city/state, using EventCacheManager
    which automatically caches results in the Event table with geohash.
    """
    import asyncio
    from backend.event_discovery import EventCacheManager

    data = request.get_json() or {}
    location = data.get("location")

    if not location:
        return jsonify({"error": "location required"}), 400

    # Parse location into city and state
    parts = [p.strip() for p in location.split(",")]
    if len(parts) < 2:
        return (
            jsonify(
                {"error": "location must be 'City, ST' format (e.g., 'Dallas, TX')"}
            ),
            400,
        )

    city = parts[0]
    state = parts[1]

    try:
        # EventCacheManager uses async/await
        # Pass db and models explicitly to avoid app context issues
        manager = EventCacheManager(
            db=db, event_model=Event, event_image_model=EventImage
        )

        # Create a new event loop and run async code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Push Flask app context for database operations
            ctx = app.app_context()
            ctx.push()

            try:
                # Run async code with app context active
                events = loop.run_until_complete(
                    manager.search_by_location(city, state)
                )
            finally:
                ctx.pop()
        finally:
            loop.close()

        return (
            jsonify(
                {
                    "events": events,
                    "location": f"{city}, {state}",
                    "count": len(events),
                    "cached": True,  # EventCacheManager auto-caches to DB
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/categories", methods=["GET"])
@jwt_required()
def get_categories():
    """Get all event categories with metadata (icons, colors, descriptions)."""
    from backend.event_discovery.event_categories import (
        EVENT_CATEGORIES,
        get_categories_by_type,
    )

    return (
        jsonify(
            {
                "categories": EVENT_CATEGORIES,
                "grouped": get_categories_by_type(),
                "count": len(EVENT_CATEGORIES),
            }
        ),
        200,
    )


@app.route("/api/events/search", methods=["POST"])
@jwt_required()
def search_events_simple():
    """Simple event search from database - returns current/future events only.

    No Facebook scraping or external calls - just fast database queries.
    """
    from datetime import datetime, timezone

    data = request.get_json() or {}
    location = data.get("location")
    category = data.get("category")
    limit = data.get("limit", 50)

    if not location:
        return jsonify({"error": "location required"}), 400

    # Parse location
    parts = [p.strip() for p in location.split(",")]
    if len(parts) < 2:
        return jsonify({"error": "location must be 'City, ST' format"}), 400

    city = parts[0]
    state = parts[1]

    try:
        # Query database directly - only future volunteer events (exclude Ticketmaster)
        query = Event.query.filter(
            Event.location_city.ilike(city),
            Event.date_start >= datetime.now(timezone.utc),
            Event.source != "Ticketmaster",  # Exclude Ticketmaster events
        )

        # Filter by category if provided
        if category and category != "All":
            query = query.filter(Event.category == category)

        # Order by date and limit
        events = query.order_by(Event.date_start.asc()).limit(limit).all()

        # Convert to dict with images
        result = []
        for event in events:
            event_dict = {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "organization": event.organization,
                "category": event.category,
                "date_start": (
                    event.date_start.isoformat() if event.date_start else None
                ),
                "venue": event.venue,
                "price": event.price,
                "location_city": event.location_city,
                "location_state": event.location_state,
                "latitude": event.latitude,
                "longitude": event.longitude,
                "contact_person": event.contact_person,
                "contact_email": event.contact_email,
                "contact_phone": event.contact_phone,
                "source": event.source,
                "url": event.url,
            }

            # Get images
            images = (
                EventImage.query.filter_by(event_id=event.id)
                .order_by(EventImage.position)
                .all()
            )
            if images:
                event_dict["image_url"] = images[0].url
                event_dict["image_urls"] = json.dumps([img.url for img in images])

            result.append(event_dict)

        return (
            jsonify(
                {
                    "events": result,
                    "location": f"{city}, {state}",
                    "count": len(result),
                    "source": "database",
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/web-search", methods=["POST"])
@jwt_required()
def web_search():
    """Search for volunteer opportunities using Google Custom Search API.

    Saves results as Event records in the database and returns them with contact info.
    """
    try:
        data = request.get_json() or {}
        query = data.get("query")
        location = data.get("location")  # Optional: {city: "...", state: "..."}

        if not query:
            return jsonify({"error": "query parameter required"}), 400

        logger.info(f"Web search request: {query}")

        # Call the Google Custom Search API
        results = search_events(query)

        # Check for errors
        if isinstance(results, dict) and "error" in results:
            logger.error(f"Web search error: {results['error']}")
            return jsonify({"error": results["error"]}), 500

        logger.info(
            f"Web search returned {len(results) if isinstance(results, list) else 0} results"
        )

        # Convert search results to Event records
        event_dicts = create_events_from_search_results(results, query, location)

        # Enrich events with contact information (limit to first 3 to avoid too many requests)
        event_dicts = enrich_events_with_contact_info(event_dicts, max_to_enrich=3)

        # Enrich events with values using Google Gemini LLM (limit to first 5)
        event_dicts = enrich_events_with_values(event_dicts, max_to_enrich=5)

        # Save events to database (using merge to avoid duplicates)
        saved_events = []
        for event_dict in event_dicts:
            # Check if event already exists
            existing_event = Event.query.get(event_dict["id"])

            if existing_event:
                # Update existing event
                for key, value in event_dict.items():
                    if key != "id":  # Don't update the ID
                        setattr(existing_event, key, value)
                saved_events.append(existing_event.to_dict())
            else:
                # Create new event
                event = Event(**event_dict)
                db.session.add(event)
                saved_events.append(event_dict)

        db.session.commit()
        logger.info(f"Saved {len(saved_events)} events to database")

        return (
            jsonify(
                {
                    "events": saved_events,
                    "query": query,
                    "count": len(saved_events),
                    "source": "google_custom_search",
                    "message": f"Found and saved {len(saved_events)} volunteer opportunities",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Web search exception: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/local-events/tonight", methods=["POST"])
@jwt_required()
def discover_tonight():
    """Discover ALL types of local events happening tonight (not just volunteer).

    Uses LocalEventsScraper to find events across multiple platforms:
    - Eventbrite
    - Meetup
    - Facebook local events
    - City event calendars

    Returns events with images, sorted by start time.
    """
    import asyncio
    from backend.event_discovery import EventCacheManager

    data = request.get_json() or {}
    location = data.get("location")
    limit = data.get("limit", 20)

    if not location:
        return jsonify({"error": "location required"}), 400

    # Parse location into city and state
    parts = [p.strip() for p in location.split(",")]
    if len(parts) < 2:
        return (
            jsonify(
                {"error": "location must be 'City, ST' format (e.g., 'Dallas, TX')"}
            ),
            400,
        )

    city = parts[0]
    state = parts[1]

    try:
        # EventCacheManager uses async/await
        manager = EventCacheManager(
            db=db, event_model=Event, event_image_model=EventImage
        )

        # Create a new event loop and run async code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Push Flask app context for database operations
            ctx = app.app_context()
            ctx.push()

            try:
                # Run async code with app context active
                events = loop.run_until_complete(
                    manager.discover_tonight(city, state, limit)
                )
            finally:
                ctx.pop()
        finally:
            loop.close()

        return (
            jsonify(
                {
                    "events": events,
                    "location": f"{city}, {state}",
                    "count": len(events),
                    "timeframe": "tonight",
                    "cached": True,  # EventCacheManager auto-caches to DB
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/events/interact", methods=["POST"])
@jwt_required()
def record_event_interaction():
    """Record user interaction with an event (like, dislike, view, attend, etc.)."""
    uid = get_jwt_identity()
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid

    data = request.get_json() or {}
    event_id = data.get("event_id")
    interaction_type = data.get(
        "interaction_type"
    )  # view, like, dislike, attend, skip, super_like
    metadata = data.get("metadata", {})

    if not event_id or not interaction_type:
        return jsonify({"error": "event_id and interaction_type required"}), 400

    # Record interaction
    interaction = UserEventInteraction(
        user_id=uid_int,
        event_id=event_id,
        interaction_type=interaction_type,
        interaction_metadata=json.dumps(metadata) if metadata else None,
    )
    db.session.add(interaction)
    db.session.commit()

    # Update user achievements based on interaction (volunteers only)
    user = User.query.get(uid_int)
    if user and user.role == "volunteer":
        from backend.event_discovery.gamification import GamificationEngine

        gamification = GamificationEngine(
            db, User, UserAchievement, UserEventInteraction
        )
        gamification.check_achievements(uid_int)

    return (
        jsonify(
            {"message": "interaction recorded", "interaction": interaction.to_dict()}
        ),
        201,
    )


@app.route("/api/events/personalized", methods=["POST"])
@jwt_required()
def get_personalized_events():
    """Get personalized event feed with match scores."""
    uid = get_jwt_identity()
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid

    data = request.get_json() or {}
    location = data.get("location")
    limit = data.get("limit", 20)

    if not location:
        return jsonify({"error": "location required"}), 400

    # Parse location
    parts = [p.strip() for p in location.split(",")]
    if len(parts) < 2:
        return (
            jsonify(
                {"error": "location must be 'City, ST' format (e.g., 'Dallas, TX')"}
            ),
            400,
        )

    city = parts[0]
    state = parts[1]

    try:
        # Get events
        import asyncio
        from backend.event_discovery import EventCacheManager

        manager = EventCacheManager(
            db=db, event_model=Event, event_image_model=EventImage
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            ctx = app.app_context()
            ctx.push()

            try:
                events = loop.run_until_complete(
                    manager.discover_tonight(
                        city, state, limit=100
                    )  # Get more events for personalization
                )
            finally:
                ctx.pop()
        finally:
            loop.close()

        # Also get Google Custom Search volunteer opportunities
        web_events = []
        try:
            web_query = f"volunteer opportunities {city} {state}"
            search_results = search_events(web_query)

            if isinstance(search_results, list) and len(search_results) > 0:
                event_dicts = create_events_from_search_results(
                    search_results, web_query, location={"city": city, "state": state}
                )
                # Enrich with values for better personalization
                event_dicts = enrich_events_with_values(event_dicts, max_to_enrich=5)
                web_events = event_dicts
                logger.info(
                    f"Personalized feed: added {len(web_events)} web search results"
                )
        except Exception as web_error:
            logger.info(
                f"Web search error in personalized feed (non-fatal): {web_error}"
            )

        # Combine database events with web events before personalization
        all_events = events + web_events
        logger.info(
            f"Personalized: {len(events)} database + {len(web_events)} web = {len(all_events)} total"
        )

        # Personalize the feed with AI
        from backend.event_discovery.personalization import PersonalizationEngine

        engine = PersonalizationEngine(db, User, Event, UserEventInteraction)

        # Use AI-powered personalization
        loop2 = asyncio.new_event_loop()
        asyncio.set_event_loop(loop2)

        try:
            ctx2 = app.app_context()
            ctx2.push()

            try:
                personalized = loop2.run_until_complete(
                    engine.get_ai_personalized_recommendations(
                        uid_int, all_events, limit=limit
                    )
                )
            finally:
                ctx2.pop()
        finally:
            loop2.close()

        return (
            jsonify(
                {
                    "events": personalized,
                    "location": f"{city}, {state}",
                    "count": len(personalized),
                    "personalized": True,
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/profile/taste", methods=["GET"])
@jwt_required()
def get_taste_profile():
    """Get user's taste profile (category preferences, etc.)."""
    uid = get_jwt_identity()
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid

    from backend.event_discovery.personalization import PersonalizationEngine

    engine = PersonalizationEngine(db, User, Event, UserEventInteraction)
    profile = engine.calculate_user_taste_profile(uid_int)

    return jsonify({"profile": profile, "user_id": uid_int}), 200


@app.route("/api/events/surprise-me", methods=["POST"])
@jwt_required()
def surprise_me():
    """Get surprise event recommendation based on mood and constraints."""
    uid = get_jwt_identity()
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid

    data = request.get_json() or {}
    location = data.get("location")
    mood = data.get(
        "mood", "adventurous"
    )  # energetic, chill, creative, social, romantic, adventurous
    budget = data.get("budget", 50)  # max price
    time_available = data.get("time_available", 3)  # hours
    adventure_level = data.get("adventure_level", "high")  # low, medium, high

    if not location:
        return jsonify({"error": "location required"}), 400

    parts = [p.strip() for p in location.split(",")]
    if len(parts) < 2:
        return jsonify({"error": "location must be 'City, ST' format"}), 400

    city = parts[0]
    state = parts[1]

    try:
        # Get events from both volunteer opportunities AND Ticketmaster
        import asyncio
        from backend.event_discovery import EventCacheManager
        from backend.ticketmaster_api import TicketmasterAPI

        manager = EventCacheManager(
            db=db, event_model=Event, event_image_model=EventImage
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            ctx = app.app_context()
            ctx.push()

            try:
                # Get volunteer events
                volunteer_events = loop.run_until_complete(
                    manager.discover_tonight(city, state, limit=50)
                )
            finally:
                ctx.pop()
        finally:
            loop.close()

        # Also fetch Ticketmaster events
        ticketmaster_events = []
        try:
            tm_api = TicketmasterAPI()
            ticketmaster_events = tm_api.get_events_for_city(city, state, limit=50)
        except Exception as tm_error:
            print(f"Ticketmaster API error (non-fatal): {tm_error}")

        # Fetch Google Custom Search volunteer opportunities
        web_events = []
        try:
            # Build mood-specific search query
            mood_keywords = {
                "energetic": "active sports fitness",
                "chill": "relaxing peaceful",
                "creative": "arts crafts creative",
                "social": "community social gathering",
                "romantic": "couples romantic",
                "adventurous": "adventure outdoor exciting",
            }
            keyword = mood_keywords.get(mood, "")
            web_query = f"volunteer opportunities {keyword} {city} {state}"

            # Search and convert to events
            search_results = search_events(web_query)
            if isinstance(search_results, list) and len(search_results) > 0:
                event_dicts = create_events_from_search_results(
                    search_results, web_query, location={"city": city, "state": state}
                )
                # Enrich with values (small batch for surprise feature)
                event_dicts = enrich_events_with_values(event_dicts, max_to_enrich=3)

                # Convert to Event objects format that SurpriseEngine expects
                for event_dict in event_dicts:
                    web_events.append(event_dict)
        except Exception as web_error:
            logger.info(f"Web search error (non-fatal): {web_error}")

        # Combine all three event sources
        all_events = volunteer_events + ticketmaster_events + web_events
        logger.info(
            f"Surprise Me: {len(volunteer_events)} volunteer + {len(ticketmaster_events)} ticketmaster + {len(web_events)} web = {len(all_events)} total"
        )

        # Generate AI-powered surprise event
        from backend.event_discovery.surprise_engine import SurpriseEngine

        surprise_engine = SurpriseEngine(db, User, Event, UserEventInteraction)

        # Use AI to generate surprise
        loop2 = asyncio.new_event_loop()
        asyncio.set_event_loop(loop2)

        try:
            ctx2 = app.app_context()
            ctx2.push()

            try:
                surprise_event = loop2.run_until_complete(
                    surprise_engine.generate_ai_surprise(
                        user_id=uid_int,
                        location=city,
                        mood=mood,
                        budget=budget,
                        time_available=time_available * 60,  # Convert hours to minutes
                        adventure_level=adventure_level,
                    )
                )
            finally:
                ctx2.pop()
        finally:
            loop2.close()

        if not surprise_event:
            return jsonify({"error": "No surprising events found"}), 404

        return (
            jsonify(
                {
                    "event": surprise_event,
                    "surprise": True,
                    "mood": mood,
                    "explanation": surprise_event.get("surprise_explanation", ""),
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/events/ticketmaster", methods=["POST"])
@jwt_required()
def get_ticketmaster_events():
    """Fetch real future events from Ticketmaster Discovery API."""
    data = request.get_json() or {}
    location = data.get("location")
    limit = data.get("limit", 50)
    classification = data.get(
        "classification"
    )  # Optional: Music, Sports, Arts & Theatre, etc.

    if not location:
        return jsonify({"error": "location required"}), 400

    parts = [p.strip() for p in location.split(",")]
    if len(parts) < 2:
        return jsonify({"error": "location must be 'City, ST' format"}), 400

    city = parts[0]
    state_code = parts[1]

    try:
        from backend.ticketmaster_api import TicketmasterAPI

        tm_api = TicketmasterAPI()

        events = tm_api.get_events_for_city(
            city=city, state_code=state_code, limit=limit, classification=classification
        )

        return (
            jsonify(
                {
                    "events": events,
                    "count": len(events),
                    "source": "Ticketmaster",
                    "city": city,
                    "state": state_code,
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/achievements", methods=["GET"])
@jwt_required()
def get_achievements():
    """Get user's achievements and progress (role-aware)."""
    uid = get_jwt_identity()
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid

    # Get user to check role
    user = User.query.get(uid_int)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Role-aware response
    if user.role == "organization":
        # Organizations get different metrics
        # Count events posted by this organization
        events_posted = Event.query.filter_by(
            organization=user.organization_name
        ).count()

        # Count total interactions with organization's events
        org_events = Event.query.filter_by(organization=user.organization_name).all()
        org_event_ids = [e.id for e in org_events]

        total_views = UserEventInteraction.query.filter(
            UserEventInteraction.event_id.in_(org_event_ids),
            UserEventInteraction.interaction_type == "view",
        ).count()

        total_likes = UserEventInteraction.query.filter(
            UserEventInteraction.event_id.in_(org_event_ids),
            UserEventInteraction.interaction_type.in_(["like", "super_like"]),
        ).count()

        total_attendees = UserEventInteraction.query.filter(
            UserEventInteraction.event_id.in_(org_event_ids),
            UserEventInteraction.interaction_type == "attend",
        ).count()

        # Unique volunteers (distinct users who interacted)
        unique_volunteers = (
            db.session.query(UserEventInteraction.user_id)
            .filter(UserEventInteraction.event_id.in_(org_event_ids))
            .distinct()
            .count()
        )

        return (
            jsonify(
                {
                    "role": "organization",
                    "organization_name": user.organization_name,
                    "metrics": {
                        "events_posted": events_posted,
                        "total_views": total_views,
                        "total_likes": total_likes,
                        "total_attendees": total_attendees,
                        "unique_volunteers": unique_volunteers,
                        "engagement_rate": (
                            round((total_likes / max(total_views, 1)) * 100, 1)
                            if total_views > 0
                            else 0
                        ),
                    },
                }
            ),
            200,
        )

    else:
        # Volunteers get achievement system
        achievements = UserAchievement.query.filter_by(user_id=uid_int).all()

        # Calculate level and XP
        from backend.event_discovery.gamification import GamificationEngine

        gamification = GamificationEngine(
            db, User, UserAchievement, UserEventInteraction
        )
        level_info = gamification.get_user_level(uid_int)

        return (
            jsonify(
                {
                    "role": "volunteer",
                    "achievements": [a.to_dict() for a in achievements],
                    "unlocked_count": sum(1 for a in achievements if a.unlocked),
                    "total_count": len(achievements),
                    "level_info": level_info,
                }
            ),
            200,
        )


from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

ADMIN_EMAILS = set(
    [
        "your@email.com",  # Replace with your email
        "dev1@email.com",  # Add your dev team emails
    ]
)
PENDING_ADMINS = set()


@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
    if email not in ADMIN_EMAILS:
        PENDING_ADMINS.add(email)
        # Optionally notify existing admins here
        return jsonify({"error": "Admin access pending manual approval"}), 403
    token = token_for(user.id)
    return jsonify({"access_token": token, "user": user.to_dict()})


@app.route("/admin/pending", methods=["GET"])
@jwt_required()
def get_pending_admins():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user or user.email not in ADMIN_EMAILS:
        return jsonify({"error": "Not authorized"}), 403
    return jsonify({"pending_admins": list(PENDING_ADMINS)})


@app.route("/admin/approve", methods=["POST"])
@jwt_required()
def approve_admin():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user or user.email not in ADMIN_EMAILS:
        return jsonify({"error": "Not authorized"}), 403
    data = request.get_json() or {}
    email = data.get("email")
    if email in PENDING_ADMINS:
        ADMIN_EMAILS.add(email)
        PENDING_ADMINS.remove(email)
        return jsonify({"approved": email})
    return jsonify({"error": "Email not pending"}), 400


app.register_blueprint(admin_bp, url_prefix="/admin")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
