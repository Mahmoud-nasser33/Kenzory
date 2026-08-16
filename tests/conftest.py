"""Shared pytest fixtures: an isolated app + database per test.

The pragmas keep SQLite from fsync-journaling every statement, which makes
test runs fast (seconds, not minutes) on Windows development machines.
"""

import pytest
from sqlalchemy import event

from kenzory import create_app
from kenzory.extensions import db
from kenzory.services.seed import run_seed


def _attach_pragmas(engine):
    @event.listens_for(engine, "connect")
    def _set_pragmas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA synchronous=OFF")
        cursor.execute("PRAGMA journal_mode=MEMORY")
        cursor.close()


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app("testing", db_uri=f"sqlite:///{db_path.as_posix()}")
    with app.app_context():
        _attach_pragmas(db.engine)
        db.create_all()
        run_seed()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_client(app):
    client = app.test_client()
    client.post(
        "/login",
        data={"identifier": "admin", "password": "Admin123!"},
    )
    return client


def make_user_client(app, username="tester", password="password123"):
    """Register and sign in a fresh user; returns (client, username)."""
    client = app.test_client()
    client.post(
        "/register",
        data={
            "username": username,
            "display_name": "Tester",
            "email": f"{username}@example.com",
            "password": password,
            "password_confirm": password,
        },
    )
    return client
