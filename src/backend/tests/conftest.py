import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set test environment BEFORE importing app
os.environ["TESTING"] = "1"
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

import pytest
from uuid import uuid4
from werkzeug.security import generate_password_hash
from app import app, db
from models import User


@pytest.fixture(scope="module")
def test_client():
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {},  # Clear production engine options
        }
    )

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()


@pytest.fixture
def create_user():
    def _create(email=None, password="password"):
        with app.app_context():
            if email is None:
                email = f"user+{uuid4().hex}@example.com"

            # Check if user already exists to avoid UNIQUE constraint errors
            existing = User.query.filter_by(email=email).first()
            if existing:
                return existing.id

            user = User(email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return user.id

    return _create


@pytest.fixture
def client(test_client):
    """Alias for tests that expect a `client` fixture name."""
    return test_client
