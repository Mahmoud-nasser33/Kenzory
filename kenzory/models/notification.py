"""Notification model — in-app alerts and optional email delivery."""

from datetime import datetime

from kenzory.extensions import db

# Notification type constants
TYPE_SUBMISSION_APPROVED = "submission_approved"
TYPE_SUBMISSION_REJECTED = "submission_rejected"
TYPE_REVIEW_RECEIVED = "review_received"
TYPE_ENDORSEMENT_RECEIVED = "endorsement_received"
TYPE_BADGE_EARNED = "badge_earned"

NOTIFICATION_TYPES = (
    TYPE_SUBMISSION_APPROVED,
    TYPE_SUBMISSION_REJECTED,
    TYPE_REVIEW_RECEIVED,
    TYPE_ENDORSEMENT_RECEIVED,
    TYPE_BADGE_EARNED,
)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    type = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False, default="")
    link = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("notifications", lazy="dynamic"))

    def __repr__(self):
        return f"<Notification {self.id} type={self.type!r} user_id={self.user_id}>"
