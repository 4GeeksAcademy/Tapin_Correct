"""Tests for password reset flow."""


def test_reset_password_flow(client, monkeypatch):
    resp = client.post("/reset-password", json={"email": "noone@example.com"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "message" in data
