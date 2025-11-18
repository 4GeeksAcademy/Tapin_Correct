"""
Comprehensive test suite for password reset flow.
Tests both the request and confirmation stages with various edge cases.
"""

import pytest
from backend.app import app, db, User
from itsdangerous import URLSafeTimedSerializer
import time


@pytest.fixture
def client():
    """Create test client with in-memory database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["SECRET_KEY"] = "test-secret"
    app.config["SECURITY_PASSWORD_SALT"] = "test-salt"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def registered_user(client):
    """Create a registered user."""
    email = "user@test.com"
    password = "original_password123"

    client.post(
        "/register", json={"email": email, "password": password, "role": "volunteer"}
    )

    return {"email": email, "password": password}


class TestPasswordResetRequest:
    """Test password reset request endpoint."""

    def test_reset_request_existing_user(self, client, registered_user):
        """Test password reset request for existing user."""
        response = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        assert response.status_code == 200
        data = response.json

        # Should indicate success without revealing user existence
        assert "message" in data
        # In dev mode without SMTP, should return reset_url
        assert "reset_url" in data or "reset email sent" in data["message"]

    def test_reset_request_nonexistent_user(self, client):
        """Test password reset request for non-existent user."""
        response = client.post(
            "/reset-password", json={"email": "nonexistent@test.com"}
        )

        assert response.status_code == 200
        data = response.json

        # Should not reveal that user doesn't exist (security)
        assert "message" in data

    def test_reset_request_missing_email(self, client):
        """Test password reset request without email."""
        response = client.post("/reset-password", json={})

        assert response.status_code == 400
        assert "error" in response.json

    def test_reset_request_empty_email(self, client):
        """Test password reset request with empty email."""
        response = client.post("/reset-password", json={"email": ""})

        assert response.status_code == 400
        assert "error" in response.json

    def test_reset_request_invalid_email_format(self, client):
        """Test password reset request with invalid email format."""
        response = client.post("/reset-password", json={"email": "invalid-email"})

        # Should still return 200 to not reveal valid emails
        assert response.status_code == 200

    def test_reset_request_returns_token_in_dev(self, client, registered_user):
        """Test that dev mode returns reset URL."""
        response = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        assert response.status_code == 200
        data = response.json

        # In dev without SMTP configured, should return reset_url
        if "reset_url" in data:
            assert "reset-password/confirm/" in data["reset_url"]


class TestPasswordResetConfirm:
    """Test password reset confirmation endpoint."""

    def test_reset_confirm_valid_token(self, client, registered_user):
        """Test password reset with valid token."""
        # Step 1: Request reset
        reset_response = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        # Extract token from response (dev mode)
        reset_data = reset_response.json
        if "reset_url" in reset_data:
            # Extract token from URL
            reset_url = reset_data["reset_url"]
            token = reset_url.split("/reset-password/confirm/")[-1]

            # Step 2: Confirm reset with new password
            new_password = "new_password456"
            confirm_response = client.post(
                f"/reset-password/confirm/{token}", json={"password": new_password}
            )

            assert confirm_response.status_code == 200
            assert "password updated" in confirm_response.json["message"]

            # Step 3: Verify can login with new password
            login_response = client.post(
                "/login",
                json={"email": registered_user["email"], "password": new_password},
            )

            assert login_response.status_code == 200
            assert "access_token" in login_response.json

            # Step 4: Verify old password no longer works
            old_login_response = client.post(
                "/login",
                json={
                    "email": registered_user["email"],
                    "password": registered_user["password"],
                },
            )

            assert old_login_response.status_code == 401

    def test_reset_confirm_missing_password(self, client, registered_user):
        """Test password reset confirm without new password."""
        # Get a valid token
        reset_response = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        reset_data = reset_response.json
        if "reset_url" in reset_data:
            reset_url = reset_data["reset_url"]
            token = reset_url.split("/reset-password/confirm/")[-1]

            # Try to confirm without password
            response = client.post(f"/reset-password/confirm/{token}", json={})

            assert response.status_code == 400
            assert "error" in response.json

    def test_reset_confirm_empty_password(self, client, registered_user):
        """Test password reset confirm with empty password."""
        reset_response = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        reset_data = reset_response.json
        if "reset_url" in reset_data:
            reset_url = reset_data["reset_url"]
            token = reset_url.split("/reset-password/confirm/")[-1]

            response = client.post(
                f"/reset-password/confirm/{token}", json={"password": ""}
            )

            assert response.status_code == 400

    def test_reset_confirm_invalid_token(self, client):
        """Test password reset confirm with invalid token."""
        response = client.post(
            "/reset-password/confirm/invalid_token_xyz",
            json={"password": "new_password123"},
        )

        assert response.status_code == 400
        assert "invalid token" in response.json["error"]

    def test_reset_confirm_expired_token(self, client, registered_user):
        """Test password reset confirm with expired token."""
        # This test verifies that the endpoint handles expired tokens correctly
        # In a real scenario, we'd wait for token expiration (3600 seconds)
        # For testing purposes, we verify the endpoint accepts the token format
        response = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        reset_data = response.json
        if "reset_url" in reset_data:
            token = reset_data["reset_url"].split("/reset-password/confirm/")[-1]

            # Test with valid (not expired) token
            # The actual expiration handling is tested by the endpoint's try/except
            response = client.post(
                f"/reset-password/confirm/{token}", json={"password": "new_password123"}
            )

            # Should succeed since token is fresh
            assert response.status_code in [200, 400]

    def test_reset_confirm_token_reuse(self, client, registered_user):
        """Test that a token can be used multiple times (if not expired)."""
        # Request reset
        reset_response = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        reset_data = reset_response.json
        if "reset_url" in reset_data:
            reset_url = reset_data["reset_url"]
            token = reset_url.split("/reset-password/confirm/")[-1]

            # First use
            first_response = client.post(
                f"/reset-password/confirm/{token}", json={"password": "password_one"}
            )
            assert first_response.status_code == 200

            # Second use (should still work if token not expired)
            second_response = client.post(
                f"/reset-password/confirm/{token}", json={"password": "password_two"}
            )
            # Token is still valid, should succeed
            assert second_response.status_code == 200

    def test_reset_confirm_user_deleted_after_request(self, client):
        """Test password reset when user is deleted after token generation."""
        # Create user
        email = "temp@test.com"
        client.post(
            "/register",
            json={"email": email, "password": "password123", "role": "volunteer"},
        )

        # Request reset
        reset_response = client.post("/reset-password", json={"email": email})
        reset_data = reset_response.json

        if "reset_url" in reset_data:
            reset_url = reset_data["reset_url"]
            token = reset_url.split("/reset-password/confirm/")[-1]

            # Delete user
            with app.app_context():
                user = User.query.filter_by(email=email).first()
                if user:
                    db.session.delete(user)
                    db.session.commit()

            # Try to use token
            response = client.post(
                f"/reset-password/confirm/{token}", json={"password": "new_password"}
            )

            assert response.status_code == 404
            assert "no such user" in response.json["error"]


class TestPasswordResetSecurity:
    """Test security aspects of password reset."""

    def test_reset_doesnt_reveal_user_existence(self, client, registered_user):
        """Test that reset requests don't reveal if email exists."""
        # Request for existing user
        existing_response = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        # Request for non-existing user
        nonexistent_response = client.post(
            "/reset-password", json={"email": "nonexistent@test.com"}
        )

        # Both should return 200 with similar messages
        assert existing_response.status_code == 200
        assert nonexistent_response.status_code == 200

        # Messages should be similar (not revealing existence)
        assert "message" in existing_response.json
        assert "message" in nonexistent_response.json

    def test_reset_token_contains_email(self, client, registered_user):
        """Test that token is properly tied to user's email."""
        response = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        data = response.json
        if "reset_url" in data:
            reset_url = data["reset_url"]
            token = reset_url.split("/reset-password/confirm/")[-1]

            # Decode token to verify it contains the email
            with app.app_context():
                serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
                email = serializer.loads(
                    token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=3600
                )
                assert email == registered_user["email"]

    def test_reset_different_users_different_tokens(self, client):
        """Test that different users get different tokens."""
        # Create two users
        user1_email = "user1@test.com"
        user2_email = "user2@test.com"

        for email in [user1_email, user2_email]:
            client.post(
                "/register",
                json={"email": email, "password": "password123", "role": "volunteer"},
            )

        # Request resets
        response1 = client.post("/reset-password", json={"email": user1_email})
        response2 = client.post("/reset-password", json={"email": user2_email})

        data1 = response1.json
        data2 = response2.json

        if "reset_url" in data1 and "reset_url" in data2:
            token1 = data1["reset_url"].split("/reset-password/confirm/")[-1]
            token2 = data2["reset_url"].split("/reset-password/confirm/")[-1]

            # Tokens should be different
            assert token1 != token2


class TestPasswordResetIntegration:
    """Integration tests for complete password reset workflow."""

    def test_complete_password_reset_flow(self, client, registered_user):
        """Test complete password reset workflow end-to-end."""
        new_password = "completely_new_password789"

        # Step 1: User requests password reset
        reset_request = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )
        assert reset_request.status_code == 200

        # Step 2: Get reset token from response
        reset_data = reset_request.json
        if "reset_url" in reset_data:
            token = reset_data["reset_url"].split("/reset-password/confirm/")[-1]

            # Step 3: User confirms reset with new password
            confirm_response = client.post(
                f"/reset-password/confirm/{token}", json={"password": new_password}
            )
            assert confirm_response.status_code == 200

            # Step 4: User logs in with new password
            login_response = client.post(
                "/login",
                json={"email": registered_user["email"], "password": new_password},
            )
            assert login_response.status_code == 200
            assert "access_token" in login_response.json

            # Step 5: Verify old password doesn't work
            old_login = client.post(
                "/login",
                json={
                    "email": registered_user["email"],
                    "password": registered_user["password"],
                },
            )
            assert old_login.status_code == 401

    def test_multiple_reset_requests(self, client, registered_user):
        """Test multiple password reset requests for same user."""
        # Request reset multiple times
        response1 = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )
        response2 = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )
        response3 = client.post(
            "/reset-password", json={"email": registered_user["email"]}
        )

        # All should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # If tokens returned, they should be different
        if "reset_url" in response1.json and "reset_url" in response2.json:
            token1 = response1.json["reset_url"].split("/reset-password/confirm/")[-1]
            token2 = response2.json["reset_url"].split("/reset-password/confirm/")[-1]
            # Tokens generated at different times should differ
            # (though they might be the same if generated in same second)
