from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
import logging
from backend.models import (
    db,
    User,
    Listing,
    Item,
    Event,
    EventImage,
    SignUp,
    Review,
    UserEventInteraction,
    UserAchievement,
    UserProfile,
)
from backend.api_routes import register_routes


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)
logger = logging.getLogger(__name__)

jwt = JWTManager()


def create_app():
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

    def _sanitize_db_uri(uri: str) -> str:
        """Sanitize a database URI by removing unsupported driver-specific
        query parameters that psycopg2 (and other DBAPI drivers) will reject.

        Example: Supabase pooler connection strings sometimes include
        `?pool_mode=session` which psycopg2 treats as an invalid DSN option.
        This helper strips `pool_mode` and leaves the rest intact.
        """
        try:
            from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

            if not uri or "pool_mode=" not in uri:
                return uri

            parsed = urlparse(uri)
            qs = dict(parse_qsl(parsed.query))
            # Remove keys that are not valid libpq options
            qs.pop("pool_mode", None)
            # If you need to remove additional params, add them here
            new_query = urlencode(qs)
            sanitized = urlunparse(parsed._replace(query=new_query))
            return sanitized
        except Exception:
            # If anything goes wrong, return original URI and let the caller
            # handle the resulting errors — safer than failing during import.
            return uri

    raw_db = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", os.environ.get("DATABASE_URL", default_db)
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = _sanitize_db_uri(raw_db)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    engine_options = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", 300)),
    }
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options
    # Secret key used for serializer tokens and other Flask features
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY", app.config["SECRET_KEY"]
    )
    app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
        "SECURITY_PASSWORD_SALT", "dev-salt"
    )

    # LLM provider selection (environment-driven). Default to 'gemini'
    # so demo runs with Gemini by default unless overridden in .env.
    app.config["LLM_PROVIDER"] = os.environ.get("LLM_PROVIDER", "gemini")

    # Configure CORS explicitly to ensure preflight OPTIONS requests succeed
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://localhost:3000",
                    "https://tapin-correct.fly.dev",
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
            }
        },
    )

    # Register blueprints
    try:
        from backend.routes.events import events_bp
    except ModuleNotFoundError:
        from routes.events import events_bp

    app.register_blueprint(events_bp, url_prefix="/events")

    # Register profile blueprint (routes under /api/... are defined in the
    # blueprint itself, so no url_prefix is necessary)
    try:
        from backend.routes.profile import profile_bp
    except ModuleNotFoundError:
        from routes.profile import profile_bp

    app.register_blueprint(profile_bp)

    # Initialize extensions
    jwt.init_app(app)
    db.init_app(app)

    # Test database connection with retry logic
    db_connected = False
    for i in range(5):
        try:
            with app.app_context():
                # Test connection
                db.engine.connect()
                print("[app.py] Database connection successful.")
                db_connected = True
            break
        except Exception as e:
            print(f"[app.py] Database connection failed (attempt {i+1}/5): {e}")
            if i == 4:
                print(
                    "[app.py] WARNING: All database connection attempts failed. App will start but database operations may fail."
                )
                app.logger.warning("Database connection failed. Using fallback mode.")
            import time

            time.sleep(2)

    # This local create_all is for dev convenience (e.g., with SQLite).
    # Production migrations are handled by the fly.toml release_command.
    if db_connected:
        with app.app_context():
            if _should_create_tables():
                app.logger.info(
                    "Creating DB tables for local dev (RUN_MIGRATIONS_ON_START or sqlite)"
                )
                try:
                    db.create_all()
                    app.logger.info("Database tables created successfully")
                except Exception as e:
                    app.logger.warning(
                        f"Failed to create database tables (they may already exist): {e}"
                    )
            else:
                app.logger.info(
                    "Skipping automatic DB table creation. "
                    "Use `fly deploy` release_command for production."
                )

    _warn_on_default_secrets(app)

    register_routes(
        app,
        db,
        User,
        Listing,
        Item,
        SignUp,
        Review,
        Event,
        EventImage,
        UserEventInteraction,
        UserAchievement,
    )

    return app


def _should_create_tables():
    """Helper to determine if `db.create_all()` should be called.

    Returns True if using SQLite or if the `RUN_MIGRATIONS_ON_START` env var
    is explicitly set to "true" or "1". This is a dev convenience and should
    be disabled in production in favor of a formal migration process.
    """
    db_uri = os.environ.get("DATABASE_URL", "")
    run_on_start = os.environ.get("RUN_MIGRATIONS_ON_START", "false").lower()
    return "sqlite" in db_uri or run_on_start in ("true", "1")


def _warn_on_default_secrets(app):
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
