"""Community voting on pending submissions."""

from kenzory.extensions import db
from kenzory.models import Submission, SubmissionVote

from conftest import make_user_client
from test_contribution import _submit_place


def _first_submission_id(app, title="The Noria of Al-Basateen"):
    with app.app_context():
        submission = Submission.query.filter_by(title=title).first()
        return submission.id


def test_review_queue_requires_login(app, client):
    assert client.get("/community-review").status_code == 302


def test_vote_requires_login(app, client):
    submitter = make_user_client(app, "submitter_v1")
    _submit_place(submitter)
    submission_id = _first_submission_id(app)
    assert client.post(f"/submissions/{submission_id}/vote").status_code == 302
    with app.app_context():
        assert SubmissionVote.query.count() == 0


def test_endorse_and_toggle(app, admin_client):
    submitter = make_user_client(app, "submitter_v2")
    _submit_place(submitter)
    submission_id = _first_submission_id(app)

    resp = admin_client.post(f"/submissions/{submission_id}/vote", follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        submission = db.session.get(Submission, submission_id)
        assert len(submission.votes) == 1

    resp = admin_client.post(f"/submissions/{submission_id}/vote", follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        submission = db.session.get(Submission, submission_id)
        assert len(submission.votes) == 0
        assert SubmissionVote.query.count() == 0


def test_cannot_vote_own_submission(app, client):
    voter = make_user_client(app, "self_voter")
    _submit_place(voter)
    submission_id = _first_submission_id(app)

    resp = voter.post(
        f"/submissions/{submission_id}/vote", follow_redirects=True
    )
    body = resp.get_data(as_text=True)
    assert "vote for your own" in body
    with app.app_context():
        submission = db.session.get(Submission, submission_id)
        assert len(submission.votes) == 0


def test_queue_lists_pending_with_counts(app, admin_client):
    submitter = make_user_client(app, "queue_submitter")
    _submit_place(submitter)
    submission_id = _first_submission_id(app)
    # A second user endorses it.
    make_user_client(app, "queue_voter").post(
        f"/submissions/{submission_id}/vote"
    )

    resp = admin_client.get("/community-review")
    body = resp.get_data(as_text=True)
    assert "The Noria of Al-Basateen" in body
    assert "1 endorsement" in body


def test_cannot_vote_nonpending_or_missing(app, admin_client):
    resp = admin_client.post("/submissions/99999/vote", follow_redirects=True)
    assert resp.status_code == 404

    # Approve a submission, then voting on it must fail.
    submitter = make_user_client(app, "approved_submitter")
    _submit_place(submitter)
    submission_id = _first_submission_id(app)
    admin_client.post(
        f"/admin/submissions/{submission_id}/approve", data={"review_note": ""}
    )
    resp = admin_client.post(f"/submissions/{submission_id}/vote", follow_redirects=True)
    assert resp.status_code == 404


def test_votes_cascade_on_user_delete(app, admin_client):
    from kenzory.models import User

    submitter = make_user_client(app, "cascade_submitter")
    _submit_place(submitter)
    submission_id = _first_submission_id(app)
    admin_client.post(f"/submissions/{submission_id}/vote")

    with app.app_context():
        user = User.query.filter_by(username="admin").first()
        db.session.delete(user)
        db.session.commit()
        assert SubmissionVote.query.count() == 0
