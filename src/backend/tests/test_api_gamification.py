import pytest
from app import app as flask_app, db as sqlalchemy_db
from models import User, Achievement, UserAchievement, UserValues
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="function")
def app():
    flask_app.config.update(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
    )

    with flask_app.app_context():
        sqlalchemy_db.create_all()
        yield flask_app
        sqlalchemy_db.drop_all()


@pytest.fixture(scope="function")
def test_client(app):
    return app.test_client()


def test_get_user_achievements(test_client):
    """
    GIVEN a Flask application
    WHEN the '/api/user/<user_id>/achievements' endpoint is requested (GET)
    THEN check that the response is valid
    """
    with test_client.application.app_context():
        new_user = User(
            email="testuser@example.com",
            password_hash=generate_password_hash(
                "password"  # pragma: allowlist secret
            ),
            is_active=True,
        )
        sqlalchemy_db.session.add(new_user)
        sqlalchemy_db.session.commit()

        response = test_client.post(
            "/login",
            json={
                "email": "testuser@example.com",
                "password": "password",  # pragma: allowlist secret
            },
        )
        access_token = response.json["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        achievement = Achievement(
            name="Test Achievement", description="A test achievement.", icon="fa-test"
        )
        sqlalchemy_db.session.add(achievement)
        sqlalchemy_db.session.commit()
        user_achievement = UserAchievement(
            user_id=new_user.id, achievement_id=achievement.id
        )
        sqlalchemy_db.session.add(user_achievement)
        sqlalchemy_db.session.commit()

        response = test_client.get(
            f"/api/user/{new_user.id}/achievements", headers=headers
        )
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["name"] == "Test Achievement"


def test_get_user_values(test_client):
    """
    GIVEN a Flask application
    WHEN the '/user/values' endpoint is requested (GET)
    THEN check that the response is valid
    """
    with test_client.application.app_context():
        new_user = User(
            email="testuser2@example.com",
            password_hash=generate_password_hash(
                "password"
            ),  # pragma: allowlist secret
            is_active=True,
        )
        sqlalchemy_db.session.add(new_user)
        sqlalchemy_db.session.commit()

        response = test_client.post(
            "/login",
            json={
                "email": "testuser2@example.com",
                "password": "password",  # pragma: allowlist secret
            },
        )
        access_token = response.json["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        user_value = UserValues(user_id=new_user.id, value="Test Value")
        sqlalchemy_db.session.add(user_value)
        sqlalchemy_db.session.commit()

        response = test_client.get("/user/values", headers=headers)
        assert response.status_code == 200
        assert len(response.json["values"]) == 1
        assert response.json["values"][0] == "Test Value"
