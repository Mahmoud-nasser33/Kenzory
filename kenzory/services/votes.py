"""Community voting on pending submissions.

Votes are simple endorsements: one per user per submission, toggled by
re-posting. Counts help reviewers prioritise well-supported records.
"""

from kenzory.extensions import db
from kenzory.models import SubmissionVote


def toggle_vote(submission, user):
    """Add the user's vote, or remove it if they already voted.

    Returns ``(voted, count)`` where ``voted`` is True when a vote exists
    after the call.
    """
    existing = SubmissionVote.query.filter_by(
        submission_id=submission.id, user_id=user.id
    ).first()
    if existing:
        db.session.delete(existing)
        voted = False
    else:
        db.session.add(SubmissionVote(submission_id=submission.id, user_id=user.id))
        voted = True
        if submission.submitted_by != user.id:
            from kenzory.services.notifications import notify_endorsement_received
            notify_endorsement_received(submission, user)
    db.session.commit()
    return voted, vote_count(submission)


def vote_count(submission):
    return len(submission.votes)


def vote_counts_map(submissions):
    """{submission_id: vote_count} for a list of submissions."""
    return {s.id: len(s.votes) for s in submissions}


def user_voted_ids(user_id, submission_ids):
    """Ids from ``submission_ids`` that ``user_id`` has voted for."""
    if not submission_ids:
        return set()
    rows = SubmissionVote.query.filter(
        SubmissionVote.user_id == user_id,
        SubmissionVote.submission_id.in_(submission_ids),
    ).all()
    return {r.submission_id for r in rows}
