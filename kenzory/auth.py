"""Authentication wiring: user loader and access-control decorators."""

from functools import wraps

from flask import abort, redirect, request, url_for
from flask_login import current_user

from kenzory.extensions import db, login_manager
from kenzory.models import User


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def login_required(view):
    """Require an authenticated user; send anonymous visitors to the login page.

    The requested path is kept in the ``next`` query parameter so users return
    to where they were after signing in.
    """

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """Require an authenticated administrator."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.full_path))
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped
