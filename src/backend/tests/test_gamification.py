import pytest
from app import app, db
from models import User, Achievement, UserAchievement, UserValues


@pytest.fixture(scope="module")
def new_user():
    user = User(
        email="testuser@example.com",
        password="password",
        is_active=True,  # pragma: allowlist secret
    )
    return user


@pytest.fixture(scope="module")
def new_achievement():
    achievement = Achievement(
        name="Test Achievement", description="A test achievement.", icon="fa-test"
    )
    return achievement


def test_new_user(test_client, new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, password, and is_active fields are defined correctly
    """
    assert new_user.email == "testuser@example.com"
    assert new_user.password == "password"  # pragma: allowlist secret
    assert new_user.is_active is True


def test_new_achievement(test_client, new_achievement):
    """
    GIVEN an Achievement model
    WHEN a new Achievement is created
    THEN check the name, description, and icon fields are defined correctly
    """
    assert new_achievement.name == "Test Achievement"
    assert new_achievement.description == "A test achievement."
    assert new_achievement.icon == "fa-test"


def test_user_achievement_relationship(test_client, new_user, new_achievement):
    """
    GIVEN a User and an Achievement
    WHEN an achievement is awarded to a user
    THEN check that the relationship is correctly established
    """
    with app.app_context():
        db.session.add(new_user)
        db.session.add(new_achievement)
        db.session.commit()

        user_achievement = UserAchievement(
            user_id=new_user.id, achievement_id=new_achievement.id
        )
        db.session.add(user_achievement)
        db.session.commit()

        assert user_achievement.user_id == new_user.id
        assert user_achievement.achievement_id == new_achievement.id


def test_user_values_relationship(test_client, new_user):
    """
    GIVEN a User
    WHEN a value is added to a user's profile
    THEN check that the relationship is correctly established
    """
    with app.app_context():
        if not db.session.get(User, new_user.id):
            db.session.add(new_user)
            db.session.commit()

        user_value = UserValues(user_id=new_user.id, value="Test Value")
        db.session.add(user_value)
        db.session.commit()

        assert user_value.user_id == new_user.id
        assert user_value.value == "Test Value"
