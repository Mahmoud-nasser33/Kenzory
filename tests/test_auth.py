"""Authentication: registration, login, logout, password reset, and access control."""

import pytest
from datetime import datetime, timedelta

from kenzory.extensions import db
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


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------


def _create_user_with_email(app, username="resetme", email="resetme@example.com"):
    """Helper: create a user directly in the DB and return it."""
    with app.app_context():
        user = User(username=username, email=email, display_name="Reset Me", role="user")
        user.set_password("oldpassword1")
        db.session.add(user)
        db.session.commit()
        return user.id


def test_forgot_password_page_renders(app, client):
    resp = client.get("/forgot-password")
    assert resp.status_code == 200
    assert b"Forgot your password" in resp.data


def test_forgot_password_redirects_authenticated(app, client):
    client.post("/login", data={"identifier": "admin", "password": "Admin123!"})
    resp = client.get("/forgot-password")
    assert resp.status_code == 302


def test_forgot_password_post_flash_message(app, client):
    resp = client.post("/forgot-password", data={"email": "nobody@example.com"})
    assert resp.status_code == 302
    follow = client.get(resp.headers["Location"])
    assert b"reset link has been sent" in follow.data


def test_forgot_password_existing_user_gets_token(app, client):
    uid = _create_user_with_email(app)
    resp = client.post("/forgot-password", data={"email": "resetme@example.com"})
    assert resp.status_code == 302
    with app.app_context():
        user = db.session.get(User, uid)
        assert user.reset_token is not None
        assert user.reset_token_expiry is not None


def test_reset_password_page_renders(app, client):
    uid = _create_user_with_email(app)
    with app.app_context():
        user = db.session.get(User, uid)
        token = user.generate_reset_token()
        db.session.commit()
    resp = client.get(f"/reset-password/{token}")
    assert resp.status_code == 200
    assert b"Set a new password" in resp.data


def test_reset_password_invalid_token(app, client):
    resp = client.get("/reset-password/invalid-token-abc")
    assert resp.status_code == 302
    follow = client.get(resp.headers["Location"])
    assert b"invalid or has expired" in follow.data


def test_reset_password_short_password(app, client):
    uid = _create_user_with_email(app)
    with app.app_context():
        user = db.session.get(User, uid)
        token = user.generate_reset_token()
        db.session.commit()
    resp = client.post(
        f"/reset-password/{token}",
        data={"password": "tiny", "password_confirm": "tiny"},
    )
    assert resp.status_code == 200
    assert b"8 characters" in resp.data


def test_reset_password_mismatch(app, client):
    uid = _create_user_with_email(app)
    with app.app_context():
        user = db.session.get(User, uid)
        token = user.generate_reset_token()
        db.session.commit()
    resp = client.post(
        f"/reset-password/{token}",
        data={"password": "newpassword1", "password_confirm": "different1"},
    )
    assert resp.status_code == 200
    assert b"do not match" in resp.data


def test_reset_password_success(app, client):
    uid = _create_user_with_email(app)
    with app.app_context():
        user = db.session.get(User, uid)
        token = user.generate_reset_token()
        db.session.commit()
    resp = client.post(
        f"/reset-password/{token}",
        data={"password": "newsecure123", "password_confirm": "newsecure123"},
    )
    assert resp.status_code == 302
    with app.app_context():
        user = db.session.get(User, uid)
        assert user.check_password("newsecure123")
        assert not user.check_password("oldpassword1")
        assert user.reset_token is None
        assert user.reset_token_expiry is None


def test_reset_token_single_use(app, client):
    uid = _create_user_with_email(app)
    with app.app_context():
        user = db.session.get(User, uid)
        token = user.generate_reset_token()
        db.session.commit()
    client.post(
        f"/reset-password/{token}",
        data={"password": "newsecure123", "password_confirm": "newsecure123"},
    )
    resp = client.get(f"/reset-password/{token}")
    assert resp.status_code == 302
    follow = client.get(resp.headers["Location"])
    assert b"invalid or has expired" in follow.data


def test_expired_token_rejected(app, client):
    uid = _create_user_with_email(app)
    with app.app_context():
        user = db.session.get(User, uid)
        user.generate_reset_token(expires_in=-1)  # already expired
        db.session.commit()
        token = user.reset_token
    resp = client.get(f"/reset-password/{token}")
    assert resp.status_code == 302
    follow = client.get(resp.headers["Location"])
    assert b"invalid or has expired" in follow.data
