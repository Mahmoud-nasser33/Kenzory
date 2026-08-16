"""Kenzory application configuration.

Configuration is selected in `create_app()` via the KENZORY_ENV variable
(development / testing / production) or an explicit config object for tests.
Secrets and deployment-specific values are read from environment variables.
"""

import os
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


def _sqlite_default(name):
    return "sqlite:///" + os.path.join(INSTANCE_DIR, name).replace("\\", "/")


def _sqlite_temp_default():
    """A writable per-instance SQLite file (used as a safe production fallback)."""
    path = os.path.join(tempfile.gettempdir(), "kenzory-fallback.db")
    return "sqlite:///" + path.replace("\\", "/")


def _normalize_db_url(url):
    """Make a provider-style DATABASE_URL usable by SQLAlchemy 2.

    Vercel Postgres / Neon / Supabase hand out ``postgres://...`` URLs, which
    SQLAlchemy does not recognise as a dialect. ``postgresql://`` is accepted
    and uses the installed psycopg2 driver by default.
    """
    if url and url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 30

    # Uploads
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB total request body
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB per image
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    COVER_FOLDER = os.path.join(BASE_DIR, "static", "img", "covers")

    # Explore pagination
    PER_PAGE = 9
    ADMIN_PER_PAGE = 15


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI or _sqlite_default("kenzory-dev.db")


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SECRET_KEY = "test-secret-key"
    CSRF_ENABLED = False  # CSRF is tested explicitly with a separate app
    SQLALCHEMY_DATABASE_URI = _sqlite_default("kenzory-test.db")
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"timeout": 30}}
    PER_PAGE = 4
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Fall back to a writable temp SQLite file when DATABASE_URL is missing so a
    # misconfigured deployment still boots and serves empty pages instead of
    # crashing every serverless function.
    _database_url = _normalize_db_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_DATABASE_URI = _database_url or _sqlite_temp_default()
    USE_FALLBACK_DB = _database_url is None
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    REMEMBER_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(config_name=None):
    if config_name is None:
        config_name = os.getenv("KENZORY_ENV", "development")
    if config_name not in CONFIG_MAP:
        raise ValueError(f"Unknown configuration: {config_name!r}")
    return CONFIG_MAP[config_name]
