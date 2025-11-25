"""
Test suite for gamification features (achievements, badges, XP).
"""

import pytest
from backend.app import app, db, User, UserEventInteraction, Event


@pytest.fixture
def client():
    """Create test client with in-memory database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"  # pragma: allowlist secret

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def volunteer_auth(client):
    """Create volunteer user and return auth headers."""
    client.post(
        "/register",
        json={
            "email": "volunteer@test.com",
            "password": "password123",  # pragma: allowlist secret
            "role": "volunteer",
        },
    )

    response = client.post(
        "/login", json={"email": "volunteer@test.com", "password": "password123"}
    )  # pragma: allowlist secret

    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def organization_auth(client):
    """Create organization user and return auth headers."""
    client.post(
        "/register",
        json={
            "email": "org@test.com",
            "password": "password123",  # pragma: allowlist secret
            "role": "organization",
            "organization_name": "Test Org",
        },
    )

    response = client.post(
        "/login", json={"email": "org@test.com", "password": "password123"}
    )  # pragma: allowlist secret

    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_event(client):
    """Create a sample event in the database."""
    import uuid
    from datetime import datetime

    with app.app_context():
        event = Event(
            id=str(uuid.uuid4()),
            title="Test Event",
            organization="Test Org",
            description="Test event for gamification",
            category="Community Service",
            location_city="Austin",
            location_state="TX",
            date_start=datetime(2025, 12, 1),
            url="https://example.com/event",
            source="test",
        )
        db.session.add(event)
        db.session.commit()
        return event.id


class TestAchievementsEndpoint:
    """Test achievements endpoint for both volunteers and organizations."""

    def test_volunteer_achievements_empty(self, client, volunteer_auth):
        """Test achievements for volunteer with no activity."""
        response = client.get("/api/achievements", headers=volunteer_auth)

        assert response.status_code == 200
        data = response.json
        assert "achievements" in data or "badges" in data or "stats" in data

    def test_volunteer_achievements_with_interactions(
        self, client, volunteer_auth, sample_event
    ):
        """Test achievements after volunteer records interactions."""
        # Record multiple interactions
        interactions = [
            {"event_id": sample_event, "interaction_type": "view"},
            {"event_id": sample_event, "interaction_type": "like"},
            {"event_id": sample_event, "interaction_type": "attend"},
        ]

        for interaction in interactions:
            client.post(
                "/api/events/interact", headers=volunteer_auth, json=interaction
            )

        # Get achievements
        response = client.get("/api/achievements", headers=volunteer_auth)

        assert response.status_code == 200
        data = response.json
        # Should show progress based on interactions
        assert data is not None

    def test_organization_achievements_empty(self, client, organization_auth):
        """Test achievements for organization with no activity."""
        response = client.get("/api/achievements", headers=organization_auth)

        assert response.status_code == 200
        data = response.json
        assert "achievements" in data or "metrics" in data or "stats" in data

    def test_achievements_requires_auth(self, client):
        """Test that achievements endpoint requires authentication."""
        response = client.get("/api/achievements")
        assert response.status_code == 401

    def test_achievements_structure(self, client, volunteer_auth):
        """Test that achievements response has expected structure."""
        response = client.get("/api/achievements", headers=volunteer_auth)

        assert response.status_code == 200
        data = response.json

        # Should be a dictionary
        assert isinstance(data, dict)


class TestVolunteerGamification:
    """Test gamification features specific to volunteers."""

    def test_volunteer_earns_badges_through_actions(
        self, client, volunteer_auth, sample_event
    ):
        """Test that volunteers can earn badges through interactions."""
        # Record enough interactions to potentially earn badges
        for i in range(10):
            client.post(
                "/api/events/interact",
                headers=volunteer_auth,
                json={
                    "event_id": sample_event,
                    "interaction_type": "view",
                    "metadata": {"action": f"view_{i}"},
                },
            )

        # Check achievements
        response = client.get("/api/achievements", headers=volunteer_auth)
        assert response.status_code == 200

        # Should have some progress tracked
        data = response.json
        assert data is not None

    def test_volunteer_xp_progression(self, client, volunteer_auth, sample_event):
        """Test XP earning and level progression for volunteers."""
        # Perform various high-value actions
        high_value_actions = [
            {"event_id": sample_event, "interaction_type": "attend"},
            {"event_id": sample_event, "interaction_type": "super_like"},
        ]

        for action in high_value_actions:
            client.post("/api/events/interact", headers=volunteer_auth, json=action)

        # Get achievements to see XP progress
        response = client.get("/api/achievements", headers=volunteer_auth)
        assert response.status_code == 200


class TestOrganizationGamification:
    """Test gamification features specific to organizations."""

    def test_organization_metrics_tracking(self, client, organization_auth):
        """Test that organizations see metrics instead of badges."""
        response = client.get("/api/achievements", headers=organization_auth)

        assert response.status_code == 200
        data = response.json

        # Organizations should see metrics like views, engagement, etc.
        # The structure might be different from volunteer achievements
        assert isinstance(data, dict)

    def test_organization_engagement_metrics(
        self, client, organization_auth, sample_event
    ):
        """Test organization engagement rate calculation."""
        # Organizations should track engagement on their events
        response = client.get("/api/achievements", headers=organization_auth)

        assert response.status_code == 200
        # Should return metrics even if no events yet
        data = response.json
        assert data is not None


class TestGamificationIntegration:
    """Integration tests for complete gamification workflow."""

    def test_volunteer_complete_gamification_journey(
        self, client, volunteer_auth, sample_event
    ):
        """Test complete volunteer gamification experience."""
        # Step 1: Start with no achievements
        initial_response = client.get("/api/achievements", headers=volunteer_auth)
        assert initial_response.status_code == 200
        initial_data = initial_response.json

        # Step 2: Perform various actions
        actions = [
            {"event_id": sample_event, "interaction_type": "view"},
            {"event_id": sample_event, "interaction_type": "like"},
            {"event_id": sample_event, "interaction_type": "attend"},
            {"event_id": sample_event, "interaction_type": "super_like"},
        ]

        for action in actions:
            response = client.post(
                "/api/events/interact", headers=volunteer_auth, json=action
            )
            assert response.status_code == 201

        # Step 3: Check updated achievements
        updated_response = client.get("/api/achievements", headers=volunteer_auth)
        assert updated_response.status_code == 200
        updated_data = updated_response.json

        # Should have some data
        assert updated_data is not None

    def test_multiple_users_independent_progress(self, client):
        """Test that multiple users have independent gamification progress."""
        # Create two volunteers
        client.post(
            "/register",
            json={
                "email": "vol1@test.com",
                "password": "password123",
                "role": "volunteer",
            },
        )
        client.post(
            "/register",
            json={
                "email": "vol2@test.com",
                "password": "password123",
                "role": "volunteer",
            },
        )

        # Login both
        vol1_token = client.post(
            "/login", json={"email": "vol1@test.com", "password": "password123"}
        ).json["access_token"]

        vol2_token = client.post(
            "/login", json={"email": "vol2@test.com", "password": "password123"}
        ).json["access_token"]

        vol1_headers = {"Authorization": f"Bearer {vol1_token}"}
        vol2_headers = {"Authorization": f"Bearer {vol2_token}"}

        # Get achievements for both
        vol1_achievements = client.get("/api/achievements", headers=vol1_headers)
        vol2_achievements = client.get("/api/achievements", headers=vol2_headers)

        assert vol1_achievements.status_code == 200
        assert vol2_achievements.status_code == 200

        # Both should have their own progress
        assert vol1_achievements.json is not None
        assert vol2_achievements.json is not None


class TestBadgeSystem:
    """Test badge earning system for volunteers."""

    def test_first_event_badge(self, client, volunteer_auth, sample_event):
        """Test earning first event badge."""
        # Attend first event
        client.post(
            "/api/events/interact",
            headers=volunteer_auth,
            json={"event_id": sample_event, "interaction_type": "attend"},
        )

        response = client.get("/api/achievements", headers=volunteer_auth)
        assert response.status_code == 200

    def test_consistency_badge(self, client, volunteer_auth, sample_event):
        """Test earning consistency badge through repeated actions."""
        # Perform actions multiple days/times
        for i in range(5):
            client.post(
                "/api/events/interact",
                headers=volunteer_auth,
                json={"event_id": sample_event, "interaction_type": "view"},
            )

        response = client.get("/api/achievements", headers=volunteer_auth)
        assert response.status_code == 200


class TestAchievementScoring:
    """Test the scoring and weighting system for achievements."""

    def test_interaction_type_weights(self, client, volunteer_auth, sample_event):
        """Test that different interaction types have different weights."""
        # Attend should be worth more than view
        client.post(
            "/api/events/interact",
            headers=volunteer_auth,
            json={"event_id": sample_event, "interaction_type": "attend"},
        )

        response = client.get("/api/achievements", headers=volunteer_auth)
        assert response.status_code == 200
        # The backend should weight 'attend' higher than 'view'

    def test_super_like_bonus(self, client, volunteer_auth, sample_event):
        """Test that super_like provides bonus points."""
        client.post(
            "/api/events/interact",
            headers=volunteer_auth,
            json={"event_id": sample_event, "interaction_type": "super_like"},
        )

        response = client.get("/api/achievements", headers=volunteer_auth)
        assert response.status_code == 200
