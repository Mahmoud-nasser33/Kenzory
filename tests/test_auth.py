"""Authentication: registration, login, logout, and access control."""

import pytest

from kenzory.models import User

from conftest import make_user_client


def test_register_creates_account(app, client):
    resp = client.post(
        "/register",
        data={
            "username": "nadia",
            "display_name": "Nadia",
            "email": "nadia@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert resp.status_code == 302
    with app.app_context():
        user = User.query.filter_by(username="nadia").first()
        assert user is not None
        assert user.email == "nadia@example.com"
        assert user.check_password("password123")
        assert not user.is_admin


def test_register_rejects_duplicate_email(app, client):
    client.post(
        "/register",
        data={
            "username": "first",
            "email": "dup@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    fresh = app.test_client()  # register auto-signs-in, so use a clean session
    resp = fresh.post(
        "/register",
        data={
            "username": "second",
            "email": "dup@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert resp.status_code == 200
    assert b"already exists" in resp.data


def test_register_rejects_short_password(app, client):
    resp = client.post(
        "/register",
        data={
            "username": "shortpw",
            "email": "short@example.com",
            "password": "tiny",
            "password_confirm": "tiny",
        },
    )
    assert resp.status_code == 200
    assert b"8 characters" in resp.data


def test_register_rejects_mismatched_passwords(app, client):
    resp = client.post(
        "/register",
        data={
            "username": "mismatch",
            "email": "mm@example.com",
            "password": "password123",
            "password_confirm": "different123",
        },
    )
    assert b"do not match" in resp.data


def test_login_by_username_and_email(app, client):
    make_user_client(app, "loginme")
    for identifier in ("loginme", "loginme@example.com"):
        c = app.test_client()
        resp = c.post("/login", data={"identifier": identifier, "password": "password123"})
        assert resp.status_code == 302


def test_login_wrong_password(app, client):
    client.post("/register", data={
        "username": "badpw",
        "email": "badpw@example.com",
        "password": "password123",
        "password_confirm": "password123",
    })
    fresh = app.test_client()  # register auto-signs-in, so use a clean session
    resp = fresh.post("/login", data={"identifier": "badpw", "password": "wrongpassword"})
    assert resp.status_code == 200
    assert b"Incorrect" in resp.data


def test_logout_requires_post(client):
    resp = client.get("/logout")
    assert resp.status_code == 405


def test_protected_pages_redirect_anonymous(client):
    for path in ("/add-place", "/submissions", "/profile", "/admin/"):
        resp = client.get(path)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


def test_next_param_open_redirect_blocked(app, client):
    resp = client.post(
        "/login?next=//evil.example.com",
        data={"identifier": "admin", "password": "Admin123!"},
    )
    assert resp.status_code == 302
    assert "evil.example.com" not in resp.headers["Location"]
