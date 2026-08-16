"""Contribution flow: adding a place, validation, and submissions page."""

from kenzory.models import Category, Submission

from conftest import make_user_client


def _submit_place(client, **overrides):
    data = {
        "title": "The Noria of Al-Basateen",
        "summary": "A working waterwheel that still lifts river water for the fields each day.",
        "description": "Stone basin, clay pots, ox-driven axle.",
        "historical_information": "Documented in the 1868 land survey of the region.",
        "location": "Al-Basateen",
        "governorate": "Aswan",
        "category": "1",
        "period": "Ottoman",
        "sources": "Local records; interview with the keeper (2021)",
        "terms": "on",
    }
    data.update(overrides)
    return client.post("/add-place", data=data)


def test_add_place_requires_login(app, client):
    resp = client.get("/add-place")
    assert resp.status_code == 302


def test_valid_submission_created(app, client):
    client = make_user_client(app, "contrib_a")
    resp = _submit_place(client)
    assert resp.status_code == 200
    assert b"has been submitted" in resp.data
    with app.app_context():
        submission = Submission.query.filter_by(title="The Noria of Al-Basateen").first()
        assert submission is not None
        assert submission.status == "pending"
        assert submission.submitter.username == "contrib_a"
        assert submission.governorate == "Aswan"


def test_submission_requires_fields(app, client):
    client = make_user_client(app, "contrib_b")
    resp = _submit_place(client, title="X", summary="", terms="")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Please enter the place name" in body
    assert "two sentences" in body


def test_submission_requires_governorate(app, client):
    client = make_user_client(app, "contrib_c")
    resp = _submit_place(client, governorate="Atlantis")
    assert resp.status_code == 200
    assert "choose a governorate" in resp.get_data(as_text=True)


def test_submissions_page_lists_own_only(app, client):
    client = make_user_client(app, "contrib_d")
    _submit_place(client)
    other = make_user_client(app, "contrib_e")
    _submit_place(other, title="Someone Else's Place")
    resp = client.get("/submissions")
    body = resp.get_data(as_text=True)
    assert "The Noria of Al-Basateen" in body
    assert "Someone Else's Place" not in body


def test_submissions_shows_status_labels(app, client):
    client = make_user_client(app, "contrib_f")
    _submit_place(client)
    resp = client.get("/submissions")
    assert "Pending review" in resp.get_data(as_text=True)


def test_anonymous_cannot_view_submissions(app, client):
    assert client.get("/submissions").status_code == 302
