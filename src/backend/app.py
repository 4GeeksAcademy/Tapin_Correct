import os
from pathlib import Path
from flask import Flask, request, jsonify, url_for, abort
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager,
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import (
    db,
    User,
    Organization,
    Item,
    Listing,
    Review,
    UserValues,
    UserAchievement,
    Achievement,
    SignUp,
)
from google_search import search_events
from auth import token_for

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
# Load .env: prefer repository root `.env`, then backend `.env` (robust for local dev).
try:
    from dotenv import load_dotenv

    repo_root = Path(__file__).resolve().parents[2]
    backend_env = Path(__file__).resolve().parent / ".env"
    env_candidates = [repo_root / ".env", backend_env]
    for env_path in env_candidates:
        if env_path.exists():
            load_dotenv(env_path)
            break
except Exception:
    pass

repo_root = Path(__file__).resolve().parents[2]
# Default to a repo-root SQLite DB when no DB URL provided. This makes local
# development and examples use `data.db` at the repository root rather than
# scattering DB files inside service directories.
default_db = "sqlite:///" + str(repo_root / "data.db")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", default_db
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Supabase connection pooling configuration for transaction mode (port 6543)
db_url = app.config["SQLALCHEMY_DATABASE_URI"]

# Skip engine options entirely for testing/SQLite
if os.environ.get("TESTING") == "1" or (
    isinstance(db_url, str) and db_url.lower().startswith("sqlite")
):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
else:
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

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-key")
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
    "SECURITY_PASSWORD_SALT", "dev-salt"
)

CORS(app)

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


def _warn_on_default_secrets():
    """Log a warning if important secret env vars are left at their dev defaults.

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
    # JWT_SECRET_KEY may default to SECRET_KEY; still warn if it's the
    # same as the dev key
    jwt_key = os.environ.get("JWT_SECRET_KEY", app.config.get("JWT_SECRET_KEY"))
    secret_key = app.config.get("SECRET_KEY")
    if not jwt_key or (jwt_key == secret_key == defaults["SECRET_KEY"]):
        missing.append("JWT_SECRET_KEY")

    if missing:
        app.logger.warning(
            "Missing or default secrets detected: %s.\n"
            "For local dev copy `.env.sample` -> `.env` and set strong values."
            " See backend/CONFIG.md for details.",
            ", ".join(sorted(set(missing))),
        )


_warn_on_default_secrets()


@app.route("/")
def index():
    return jsonify({"message": "Tapin Backend API Root"})


@app.route("/api/health", methods=["GET"])
def api_health():
    """Enhanced health check including database connectivity."""
    health_status = {"status": "ok", "components": {}}

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
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "user already exists"}), 400
    pw_hash = generate_password_hash(password)
    user = User(email=email, password_hash=pw_hash, is_active=True)
    db.session.add(user)
    db.session.commit()
    from auth import token_pair

    tokens = token_pair(user)
    return jsonify({"message": "user created", "user": user.to_dict(), **tokens}), 201


@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401
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
    try:
        uid_int = int(uid)
    except Exception:
        uid_int = uid
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
        msg = "If an account exists for that email, a reset link has been sent."
        return jsonify({"message": msg})

    serializer = get_serializer()
    token = serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])
    reset_url = url_for("confirm_reset", token=token, _external=True)

    sent, info = send_reset_email(email, reset_url)
    if sent:
        return jsonify({"message": "reset email sent"})
    else:
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
    q = request.args.get("q", type=str)
    location = request.args.get("location", type=str)

    query = Listing.query
    if q:
        categories = ["Community", "Environment", "Education", "Health", "Animals"]
        if q.lower() in [c.lower() for c in categories]:
            query = query.filter(Listing.category.ilike(q))
        else:
            like = f"%{q}%"
            title_match = Listing.title.ilike(like)
            desc_match = Listing.description.ilike(like)
            query = query.filter(title_match | desc_match)
    if location:
        query = query.filter(Listing.location.ilike(f"%{location}%"))

    listings = query.order_by(Listing.created_at.desc()).all()
    return jsonify([listing.to_dict() for listing in listings])


@app.route("/listings", methods=["POST"])
@jwt_required()
def create_listing():
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title required"}), 400
    owner_id = int(get_jwt_identity())
    category = data.get("category")
    allowed = ["Community", "Environment", "Education", "Health", "Animals"]
    if category and category not in allowed:
        return jsonify({"error": "invalid category"}), 400

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
    listing = db.session.get(Listing, id) or abort(404)
    return jsonify(listing.to_dict())


@app.route("/listings/<int:id>", methods=["PUT"])
@jwt_required()
def update_listing(id):
    listing = db.session.get(Listing, id) or abort(404)
    owner_id = int(get_jwt_identity())
    if listing.owner_id != owner_id:
        return jsonify({"error": "unauthorized - you are not the owner"}), 403
    data = request.get_json() or {}
    listing.title = data.get("title", listing.title)
    listing.description = data.get("description", listing.description)
    listing.location = data.get("location", listing.location)
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
    listing = db.session.get(Listing, id) or abort(404)
    owner_id = int(get_jwt_identity())
    if listing.owner_id != owner_id:
        return jsonify({"error": "unauthorized - you are not the owner"}), 403
    db.session.delete(listing)
    db.session.commit()
    return jsonify({"message": "deleted"})


@app.route("/listings/<int:id>/signup", methods=["POST"])
@jwt_required()
def signup_for_listing(id):
    """Volunteer signs up for a listing."""
    _ = db.session.get(Listing, id) or abort(404)
    user_id = int(get_jwt_identity())

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
    listing = db.session.get(Listing, id) or abort(404)
    owner_id = int(get_jwt_identity())

    if listing.owner_id != owner_id:
        return jsonify({"error": "unauthorized - you are not the owner"}), 403

    signups = (
        SignUp.query.filter_by(listing_id=id).order_by(SignUp.created_at.desc()).all()
    )

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
    """Update sign-up status (owner can accept/decline, volunteer can cancel)."""
    signup = db.session.get(SignUp, id) or abort(404)
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "status required"}), 400

    listing = db.session.get(Listing, signup.listing_id)
    if not listing:
        return jsonify({"error": "listing not found"}), 404

    if listing.owner_id == user_id:
        if new_status not in ["accepted", "declined"]:
            return (
                jsonify({"error": "owner can only set status to accepted or declined"}),
                400,
            )
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
    _ = db.session.get(Listing, id) or abort(404)
    user_id = int(get_jwt_identity())

    existing = Review.query.filter_by(user_id=user_id, listing_id=id).first()
    if existing:
        return jsonify({"error": "you have already reviewed this listing"}), 400

    data = request.get_json() or {}
    rating = data.get("rating")

    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "rating must be an integer between 1 and 5"}), 400

    review = Review(
        user_id=user_id, listing_id=id, rating=rating, comment=data.get("comment")
    )
    db.session.add(review)
    db.session.commit()

    return jsonify(review.to_dict()), 201


@app.route("/listings/<int:id>/reviews", methods=["GET"])
def get_listing_reviews(id):
    """Get all reviews for a listing."""
    _ = db.session.get(Listing, id) or abort(404)
    reviews = (
        Review.query.filter_by(listing_id=id).order_by(Review.created_at.desc()).all()
    )

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
    _ = db.session.get(Listing, id) or abort(404)
    reviews = Review.query.filter_by(listing_id=id).all()

    if not reviews:
        return jsonify({"average_rating": 0, "review_count": 0})

    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    return jsonify(
        {"average_rating": round(avg_rating, 1), "review_count": len(reviews)}
    )


@app.route("/user/values", methods=["GET"])
@jwt_required()
def get_user_values():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))
    return jsonify({"values": [v.value for v in user.values]}), 200


@app.route("/user/values", methods=["POST"])
@jwt_required()
def add_user_value():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))
    data = request.get_json()
    value = UserValues(user_id=user.id, value=data["value"])
    db.session.add(value)
    db.session.commit()
    return jsonify({"msg": "Value added successfully"}), 200


@app.route("/user/values", methods=["DELETE"])
@jwt_required()
def delete_user_value():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))
    data = request.get_json()
    value = UserValues.query.filter_by(user_id=user.id, value=data["value"]).first()
    db.session.delete(value)
    db.session.commit()
    return jsonify({"msg": "Value deleted successfully"}), 200


@app.route("/api/search/events", methods=["GET"])
def search_external_events():
    query = request.args.get("q")
    category = request.args.get("category")

    if not query:
        return jsonify({"error": "Missing search query"}), 400

    search_query = f"{query} in {category}" if category and category != "All" else query

    results = search_events(search_query)
    return jsonify(results), 200


@app.route("/api/user/<int:user_id>/achievements", methods=["GET"])
@jwt_required()
def get_user_achievements(user_id):
    """Gets all achievements for a specific user."""
    current_user_id = get_jwt_identity()

    user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()

    if not user_achievements:
        return jsonify([]), 200

    achievements_data = []
    for ua in user_achievements:
        achievement = db.session.get(Achievement, ua.achievement_id)
        if achievement:
            achievements_data.append(
                {
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon,
                }
            )

    return jsonify(achievements_data), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
