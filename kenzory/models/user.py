"""User model."""

import secrets
from datetime import datetime, timedelta

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from kenzory.extensions import db

ROLE_USER = "user"
ROLE_ADMIN = "admin"
ROLES = (ROLE_USER, ROLE_ADMIN)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(120), nullable=False, default="")
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text, nullable=False, default="")
    level = db.Column(db.String(40), nullable=False, default="Contributor")
    role = db.Column(db.String(20), nullable=False, default=ROLE_USER)

    reset_token = db.Column(db.String(64), nullable=True, index=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    places = db.relationship(
        "HeritagePlace",
        backref="creator",
        lazy=True,
        foreign_keys="HeritagePlace.created_by",
    )
    submissions = db.relationship(
        "Submission",
        backref="submitter",
        lazy=True,
        foreign_keys="Submission.submitted_by",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expires_in=3600):
        """Generate a secure reset token valid for *expires_in* seconds (default 1 h)."""
        self.reset_token = secrets.token_urlsafe(48)
        self.reset_token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        return self.reset_token

    def validate_reset_token(self, token):
        """Return True if *token* matches and has not expired."""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if datetime.utcnow() > self.reset_token_expiry:
            self.clear_reset_token()
            return False
        return secrets.compare_digest(self.reset_token, token)

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @property
    def display(self):
        return self.display_name or self.username

    @property
    def initials(self):
        parts = [p for p in self.display.split() if p]
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.display[:2].upper()

    @property
    def approved_place_count(self):
        return sum(1 for p in self.places if p.status == "approved")

    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def endorsement_count(self):
        from kenzory.models.vote import SubmissionVote
        return SubmissionVote.query.filter_by(user_id=self.id).count()

    def __repr__(self):
        return f"<User {self.username!r}>"
