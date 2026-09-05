"""Kenzory application configuration.

Configuration is selected in `create_app()` via the KENZORY_ENV variable
(development / testing / production) or an explicit config object for tests.
Secrets and deployment-specific values are read from environment variables —
never hardcode production values.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

_DEFAULT_SECRET = "change-me-in-production"


def _sqlite_default(name):
    return "sqlite:///" + os.path.join(INSTANCE_DIR, name).replace("\\", "/")


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", _DEFAULT_SECRET)

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 30
    PREFERRED_URL_SCHEME = "http"

    # Uploads
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB total request body
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB per image
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    COVER_FOLDER = os.path.join(BASE_DIR, "static", "img", "covers")

    # Explore pagination
    PER_PAGE = 9
    ADMIN_PER_PAGE = 15

    # Email (Flask-Mail)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@kenzory.org")
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "true").lower() == "true"


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
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    REMEMBER_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"


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


def validate_production(app):
    """Fail fast when production is missing security-critical settings."""
    problems = []
    secret = app.config.get("SECRET_KEY")
    if not secret or secret == _DEFAULT_SECRET:
        problems.append(
            "Set the SECRET_KEY environment variable to a long random value "
            "before starting."
        )
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        problems.append(
            "Set the DATABASE_URL environment variable (e.g. a PostgreSQL "
            "connection string) before starting."
        )
    if problems:
        raise RuntimeError("Production configuration is incomplete: " + "; ".join(problems))