"""Admin moderation: dashboards, approval, rejection, access control."""

from kenzory.extensions import db
from kenzory.models import HeritagePlace, Submission

from conftest import make_user_client
from test_contribution import _submit_place


def test_admin_pages_require_admin(app, client):
    normal = make_user_client(app, "regular_user")
    for path in ("/admin/", "/admin/submissions", "/admin/places", "/admin/users"):
        assert normal.get(path).status_code == 403


def test_admin_dashboard(app, admin_client):
    resp = admin_client.get("/admin/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Pending review" in body or "Total places" in body


def test_admin_lists_submissions(app, admin_client):
    make_user_client(app, "contrib_admin_a").post(
        "/add-place",
        data={
            "title": "Pending monument",
            "summary": "A watchtower overlooking the river with carved stone lintels.",
            "location": "Qena",
            "governorate": "Qena",
            "category": "1",
            "terms": "on",
        },
    )
    resp = admin_client.get("/admin/submissions?status=pending")
    assert resp.status_code == 200
    assert "Pending monument" in resp.get_data(as_text=True)


def test_admin_approves_submission(app, admin_client):
    client = make_user_client(app, "contrib_admin_b")
    _submit_place(client)
    with app.app_context():
        submission = Submission.query.filter_by(title="The Noria of Al-Basateen").first()
        sub_id = submission.id
        assert submission.status == "pending"

    resp = admin_client.post(
        f"/admin/submissions/{sub_id}/approve", data={"review_note": "Looks good"}
    )
    assert resp.status_code == 302

    with app.app_context():
        submission = db.session.get(Submission, sub_id)
        place = HeritagePlace.query.filter_by(title="The Noria of Al-Basateen").first()
        assert submission.status == "approved"
        assert place is not None
        assert place.status == "approved"
        assert place.slug.startswith("the-noria")
        assert place.governorate == "Aswan"


def test_admin_rejects_submission(app, admin_client):
    client = make_user_client(app, "contrib_admin_c")
    _submit_place(client, title="Dubious claim site")
    with app.app_context():
        submission = Submission.query.filter_by(title="Dubious claim site").first()
        sub_id = submission.id

    resp = admin_client.post(
        f"/admin/submissions/{sub_id}/reject", data={"review_note": "Cannot verify"}
    )
    assert resp.status_code == 302

    with app.app_context():
        submission = db.session.get(Submission, sub_id)
        assert submission.status == "rejected"
        assert submission.review_note == "Cannot verify"
        assert HeritagePlace.query.filter_by(title="Dubious claim site").first() is None


def test_admin_places_page(app, admin_client):
    resp = admin_client.get("/admin/places")
    assert resp.status_code == 200


def test_admin_users_page(app, admin_client):
    resp = admin_client.get("/admin/users")
    assert resp.status_code == 200
