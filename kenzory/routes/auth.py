"""Authentication routes: register, login, logout, password reset."""

import logging
import re
from urllib.parse import urljoin, urlparse

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from flask_mail import Message

from kenzory.extensions import db, mail
from kenzory.models import User

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

log = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


def _safe_next(target):
    """Only allow same-origin relative redirects for the ``next`` param."""
    if not target:
        return None
    host = urlparse(request.host_url)
    ref = urlparse(urljoin(request.host_url, target))
    if ref.scheme in ("http", "https") and ref.netloc != host.netloc:
        return None
    if target.startswith("//"):
        return None
    return target


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = {}
    errors = {}
    if request.method == "POST":
        form = {
            "username": request.form.get("username", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "display_name": request.form.get("display_name", "").strip(),
            "password": request.form.get("password", ""),
            "password_confirm": request.form.get("password_confirm", ""),
        }

        errors = validate_registration(form)
        if not errors:
            user = User(
                username=form["username"],
                email=form["email"],
                display_name=form["display_name"],
                role="user",
            )
            user.set_password(form["password"])
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Welcome to Kenzory — your account is ready.", "success")
            return redirect(url_for("main.index"))

    return render_template("auth/register.html", form=form, errors=errors)


def validate_registration(form):
    errors = {}
    username = form["username"]
    email = form["email"]
    password = form["password"]

    if not USERNAME_RE.match(username):
        errors["username"] = (
            "Username must be 3–20 characters using letters, numbers or underscores."
        )
    elif User.query.filter_by(username=username).first():
        errors["username"] = "That username is already taken."

    if not EMAIL_RE.match(email):
        errors["email"] = "Please enter a valid email address."
    elif User.query.filter_by(email=email).first():
        errors["email"] = "An account with that email already exists."

    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters long."
    elif password != form.get("password_confirm"):
        errors["password_confirm"] = "Passwords do not match."

    return errors


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    error = None
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = (
            User.query.filter(
                (User.username == identifier) | (User.email == identifier.lower())
            ).first()
        )
        if user is None or not user.check_password(password):
            error = "Incorrect username/email or password."
        else:
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.display}.", "success")
            nxt = _safe_next(request.args.get("next"))
            return redirect(nxt or url_for("main.index"))

    return render_template(
        "auth/login.html",
        error=error,
        identifier=request.form.get("identifier", "") if request.method == "POST" else "",
        next=_safe_next(request.args.get("next")),
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            _send_reset_email(user, token)
        flash(
            "If an account with that email exists, a reset link has been sent.",
            "info",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = User.query.filter_by(reset_token=token).first()
    if user is None or not user.validate_reset_token(token):
        flash("This reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    errors = {}
    if request.method == "POST":
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if len(password) < 8:
            errors["password"] = "Password must be at least 8 characters long."
        elif password != password_confirm:
            errors["password_confirm"] = "Passwords do not match."

        if not errors:
            user.set_password(password)
            user.clear_reset_token()
            db.session.commit()
            flash("Your password has been reset. You can now sign in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token, errors=errors)


def _send_reset_email(user, token):
    """Send the password-reset email. Best-effort, never raises."""
    try:
        from flask import current_app

        if current_app.config.get("MAIL_SUPPRESS_SEND"):
            return
        reset_url = url_for("auth.reset_password", token=token, _external=True)
        msg = Message(
            subject="Reset your Kenzory password",
            recipients=[user.email],
        )
        msg.html = render_template(
            "emails/password_reset.html", user=user, reset_url=reset_url
        )
        msg.body = (
            f"Hi {user.display},\n\n"
            f"Click the link below to reset your password:\n{reset_url}\n\n"
            f"If you didn't request this, you can ignore this email."
        )
        mail.send(msg)
    except Exception:
        log.exception("Failed to send password-reset email to user %s", user.id)
