"""Notification system: creation, delivery, UI routes, and integration."""

from kenzory.extensions import db
from kenzory.models import Notification, Submission, User
from kenzory.services.notifications import (
    all_notifications,
    create_notification,
    mark_all_read,
    mark_read,
    notify_badge_earned,
    notify_endorsement_received,
    notify_review_received,
    notify_submission_approved,
    notify_submission_rejected,
    unread_count,
)

from conftest import make_user_client
from test_contribution import _submit_place


# ---------------------------------------------------------------------------
# Service-level tests
# ---------------------------------------------------------------------------


def test_create_notification(app):
    with app.app_context():
        user = User.query.first()
        notif = create_notification(user.id, "badge_earned", "Test title", "Test message", link="/profile")
        assert notif.id is not None
        assert notif.is_read is False
        assert notif.link == "/profile"


def test_unread_count(app):
    with app.app_context():
        user = User.query.first()
        create_notification(user.id, "badge_earned", "A", "B")
        create_notification(user.id, "badge_earned", "C", "D")
        assert unread_count(user.id) == 2
        mark_all_read(user.id)
        assert unread_count(user.id) == 0


def test_mark_read_single(app):
    with app.app_context():
        user = User.query.first()
        notif = create_notification(user.id, "badge_earned", "X", "Y")
        db.session.commit()
        assert unread_count(user.id) == 1
        mark_read(notif.id, user.id)
        db.session.commit()
        assert unread_count(user.id) == 0


def test_mark_all_read(app):
    with app.app_context():
        user = User.query.first()
        for i in range(5):
            create_notification(user.id, "badge_earned", f"T{i}", f"M{i}")
        db.session.commit()
        assert unread_count(user.id) == 5
        mark_all_read(user.id)
        db.session.commit()
        assert unread_count(user.id) == 0


def test_recent_notifications(app):
    with app.app_context():
        user = User.query.first()
        for i in range(3):
            create_notification(user.id, "badge_earned", f"T{i}", f"M{i}")
        db.session.commit()
        notifs = all_notifications(user.id)
        assert len(notifs.items) == 3


# ---------------------------------------------------------------------------
# Integration: approve/reject triggers notification
# ---------------------------------------------------------------------------


def test_approval_creates_notification(app, admin_client):
    client = make_user_client(app, "notif_approve")
    _submit_place(client, title="Approval test place")
    with app.app_context():
        submission = Submission.query.filter_by(title="Approval test place").first()
        sub_id = submission.id

    admin_client.post(f"/admin/submissions/{sub_id}/approve", data={})

    with app.app_context():
        submission = db.session.get(Submission, sub_id)
        notifs = Notification.query.filter_by(
            user_id=submission.submitted_by, type="submission_approved"
        ).all()
        assert len(notifs) >= 1
        assert "approved" in notifs[0].title.lower()


def test_rejection_creates_notification(app, admin_client):
    client = make_user_client(app, "notif_reject")
    _submit_place(client, title="Rejection test place")
    with app.app_context():
        submission = Submission.query.filter_by(title="Rejection test place").first()
        sub_id = submission.id

    admin_client.post(
        f"/admin/submissions/{sub_id}/reject", data={"review_note": "Nope"}
    )

    with app.app_context():
        submission = db.session.get(Submission, sub_id)
        notifs = Notification.query.filter_by(
            user_id=submission.submitted_by, type="submission_rejected"
        ).all()
        assert len(notifs) >= 1


# ---------------------------------------------------------------------------
# Integration: review triggers notification
# ---------------------------------------------------------------------------


def test_review_creates_notification(app, admin_client):
    """Approve a place, then have another user review it."""
    client = make_user_client(app, "notif_reviewer_src")
    _submit_place(client, title="Review notif place")
    with app.app_context():
        submission = Submission.query.filter_by(title="Review notif place").first()
        sub_id = submission.id

    admin_client.post(f"/admin/submissions/{sub_id}/approve", data={})

    with app.app_context():
        from kenzory.models import HeritagePlace

        place = HeritagePlace.query.filter_by(title="Review notif place").first()
        place_slug = place.slug
        place_owner_id = place.created_by

    reviewer = make_user_client(app, "notif_reviewer_b")
    reviewer.post(
        f"/place/{place_slug}/review",
        data={"rating": "5", "body": "Wonderful place"},
    )

    with app.app_context():
        notifs = Notification.query.filter_by(
            user_id=place_owner_id, type="review_received"
        ).all()
        assert len(notifs) >= 1


# ---------------------------------------------------------------------------
# Integration: endorsement triggers notification
# ---------------------------------------------------------------------------


def test_endorsement_creates_notification(app, admin_client):
    client = make_user_client(app, "notif_endorsee")
    _submit_place(client, title="Endorse notif place")
    with app.app_context():
        submission = Submission.query.filter_by(title="Endorse notif place").first()
        sub_id = submission.id
        owner_id = submission.submitted_by

    endorser = make_user_client(app, "notif_endorser")
    endorser.post(f"/submissions/{sub_id}/vote")

    with app.app_context():
        notifs = Notification.query.filter_by(
            user_id=owner_id, type="endorsement_received"
        ).all()
        assert len(notifs) >= 1


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------


def test_notifications_page_requires_login(app, client):
    resp = client.get("/notifications/")
    assert resp.status_code == 302


def test_notifications_page_renders(app, admin_client):
    resp = admin_client.get("/notifications/")
    assert resp.status_code == 200
    assert "Notifications" in resp.get_data(as_text=True)


def test_mark_all_read_route(app, admin_client):
    with app.app_context():
        user = User.query.filter_by(role="admin").first()
        create_notification(user.id, "badge_earned", "Test", "Body")
        db.session.commit()

    resp = admin_client.post("/notifications/read-all")
    assert resp.status_code == 302


def test_unread_count_api(app, admin_client):
    with app.app_context():
        user = User.query.filter_by(role="admin").first()
        create_notification(user.id, "badge_earned", "X", "Y")
        db.session.commit()

    resp = admin_client.get("/notifications/unread-count")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] >= 1


def test_recent_api(app, admin_client):
    resp = admin_client.get("/notifications/recent")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "notifications" in data
