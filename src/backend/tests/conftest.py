import sys
import os
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    ),
)
import pytest  # noqa: E402
from uuid import uuid4  # noqa: E402
from app import app, db, User  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

# Ensure tests do not call premium LLM providers by default
# Allow overriding by explicitly setting LLM_PROVIDER in the environment
os.environ.setdefault("LLM_PROVIDER", "mock")


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        # Clean up DB between tests to ensure isolation
        db.session.remove()
        db.drop_all()


@pytest.fixture
def create_user():
    def _create(email=None, password="password"):
        with app.app_context():
            if email is None:
                email = f"user+{uuid4().hex}@example.com"
            user = User(
                email=email,
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            db.session.commit()
            return user.id

    return _create
