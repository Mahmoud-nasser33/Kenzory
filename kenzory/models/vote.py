"""SubmissionVote — a community endorsement of a pending submission.

One vote per user per submission (unique constraint); posting again toggles
the vote off. Vote counts surface on the community review queue and in the
admin dashboard to help reviewers prioritise well-supported records.
"""

from datetime import datetime

from kenzory.extensions import db


class SubmissionVote(db.Model):
    __tablename__ = "submission_votes"
    __table_args__ = (
        db.UniqueConstraint("submission_id", "user_id", name="uq_votes_submission_user"),
    )

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(
        db.Integer,
        db.ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    submission = db.relationship("Submission", backref=db.backref("votes", cascade="all, delete-orphan"))
    user = db.relationship(
        "User",
        backref=db.backref("submission_votes", cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<SubmissionVote submission={self.submission_id} user={self.user_id}>"
