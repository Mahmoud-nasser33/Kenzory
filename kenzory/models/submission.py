"""Submission model — community-contributed places awaiting moderation.

Normal users cannot publish places directly. They create a Submission with
status "pending"; an admin approves (creating a published HeritagePlace) or
rejects it with a review note.
"""

from datetime import datetime

from kenzory.extensions import db

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
SUBMISSION_STATUSES = (STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED)


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    historical_information = db.Column(db.Text)
    sources = db.Column(db.Text)
    location = db.Column(db.String(255), nullable=False, default="")
    governorate = db.Column(db.String(120), nullable=False, index=True)
    period = db.Column(db.String(120))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    images = db.Column(db.JSON, default=list)
    # Maps image path -> caption text, for photos uploaded with captions.
    image_captions = db.Column(db.JSON, default=dict)

    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True
    )
    submitted_by = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status = db.Column(
        db.String(20), nullable=False, default=STATUS_PENDING, index=True
    )
    review_note = db.Column(db.Text)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    reviewed_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Submission {self.id} {self.title!r} {self.status}>"
