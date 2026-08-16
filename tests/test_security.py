"""CSRF protection and security behaviour (explicitly with CSRF enabled)."""

import pytest

from kenzory import create_app
from kenzory.extensions import db
from kenzory.services.seed import run_seed


from conftest import _attach_pragmas


@pytest.fixture()
def csrf_app(tmp_path):
    db_path = tmp_path / "csrf.db"
    app = create_app("testing", db_uri=f"sqlite:///{db_path.as_posix()}")
    app.config["CSRF_ENABLED"] = True
    with app.app_context():
        _attach_pragmas(db.engine)
        db.create_all()
        run_seed()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_post_without_csrf_rejected(csrf_app):
    client = csrf_app.test_client()
    resp = client.post("/register", data={"username": "x", "email": "x@example.com"})
    assert resp.status_code == 400


def test_post_with_wrong_csrf_rejected(csrf_app):
    client = csrf_app.test_client()
    resp = client.post("/register", data={"csrf_token": "not-a-real-token"})
    assert resp.status_code == 400


def test_post_with_valid_csrf_accepted(csrf_app):
    client = csrf_app.test_client()
    html = client.get("/register").get_data(as_text=True)
    import re

    token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    resp = client.post(
        "/register",
        data={
            "csrf_token": token,
            "username": "csrfuser",
            "email": "csrf@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert resp.status_code == 302


def test_login_form_embeds_csrf(csrf_app):
    html = csrf_app.test_client().get("/login").get_data(as_text=True)
    assert 'name="csrf_token"' in html
