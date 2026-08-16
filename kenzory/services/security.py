"""Security helpers: CSRF protection and safe slug generation.

CSRF is implemented without an extra dependency: a per-session token stored
in the secure cookie, rendered into every POST form (or read from the
X-CSRF-Token header for fetch requests) and verified on every state-changing
request.
"""

import hmac
import re
import secrets
from datetime import datetime

from flask import abort, current_app, request, session

CSRF_SESSION_KEY = "_csrf_token"
_UNSAFE_METHODS = ("POST", "PUT", "PATCH", "DELETE")


def get_csrf_token():
    """Return the session CSRF token, creating one on first use."""
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_hex(32)
        session[CSRF_SESSION_KEY] = token
    return token


def _csrf_enabled():
    return current_app.config.get("CSRF_ENABLED", True)


def protect_csrf():
    """before_request hook that validates the token for unsafe methods."""
    if request.method not in _UNSAFE_METHODS:
        return None
    if not _csrf_enabled():
        return None
    token = session.get(CSRF_SESSION_KEY)
    supplied = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    if not token or not supplied or not hmac.compare_digest(str(token), str(supplied)):
        abort(400, description="Your session expired. Please go back and try again.")
    return None


def slugify(value, max_length=120):
    """Turn arbitrary text into a URL-safe slug."""
    text = re.sub(r"[^\w\s-]", "", str(value).lower().strip())
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:max_length].strip("-") or "untitled"


def utcnow():
    return datetime.utcnow()
