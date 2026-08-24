"""Contribution flow: adding a place, validation, and submissions page.

Also covers the richer-contribution features: captioned photo uploads and
editing existing records (creator or admin only).
"""

from kenzory.extensions import db
from kenzory.models import Category, HeritagePlace, Submission

from conftest import login_client, make_user_client, png_file


SEED_PASSWORD = "Kenzory123!"


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


# ---------------------------------------------------------------------------
# Captioned photo uploads
# ---------------------------------------------------------------------------


def test_submission_stores_photo_captions(app, client):
    client = make_user_client(app, "captioner")
    resp = client.post(
        "/add-place",
        data={
            "title": "Captioned Gateway",
            "summary": "An old city gate whose inscriptions survive on the northern side.",
            "location": "Rosetta",
            "governorate": "Beheira",
            "category": "1",
            "terms": "on",
            "photos": [png_file("gate.png")],
            "photo_captions": ["The gate at dawn"],
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        submission = Submission.query.filter_by(title="Captioned Gateway").first()
        assert submission is not None
        assert len(submission.images) == 1
        assert submission.image_captions[submission.images[0]] == "The gate at dawn"


# ---------------------------------------------------------------------------
# Editing existing places
# ---------------------------------------------------------------------------


def _seeded_place(app):
    with app.app_context():
        place = HeritagePlace.query.filter_by(slug="deir-al-qusayr").first()
        assert place is not None
        return place.slug


def test_edit_place_requires_login(app, client):
    slug = _seeded_place(app)
    assert client.get(f"/place/{slug}/edit").status_code == 302


def test_edit_place_forbidden_for_non_owner(app, client):
    slug = _seeded_place(app)
    stranger = make_user_client(app, "not_the_owner")
    assert stranger.get(f"/place/{slug}/edit").status_code == 403
    resp = stranger.post(
        f"/place/{slug}/edit", data={"title": "Hacked Title Here"}
    )
    assert resp.status_code == 403
    with app.app_context():
        place = HeritagePlace.query.filter_by(slug=slug).first()
        assert place.title != "Hacked Title Here"


def test_owner_sees_edit_form(app, client):
    slug = _seeded_place(app)
    owner = login_client(app, "mahmoud", SEED_PASSWORD)
    resp = owner.get(f"/place/{slug}/edit")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Current photos" in body
    assert "Deir al-Qusayr" in body or "deir-al-qusayr" in body


def test_owner_can_edit_place_fields(app, client):
    slug = _seeded_place(app)
    owner = login_client(app, "mahmoud", SEED_PASSWORD)
    with app.app_context():
        gallery = HeritagePlace.query.filter_by(slug=slug).first().gallery

    resp = owner.post(
        f"/place/{slug}/edit",
        data={
            "title": "Deir al-Qusayr — Updated",
            "summary": "A refreshed summary that is definitely long enough to pass validation checks.",
            "description": "Updated description.",
            "historical_information": "New historical note.",
            "location": "Qusayr",
            "governorate": "Aswan",
            "period": "",
            "sources": "Field visit (2026)",
            "category": "1",
            "latitude": "24.5",
            "longitude": "32.9",
            "path_0": gallery[0],
            "keep_0": "on",
            "caption_0": "West façade at noon",
            "terms": "on",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        place = HeritagePlace.query.filter_by(slug=slug).first()
        assert place.title == "Deir al-Qusayr — Updated"
        assert place.summary.startswith("A refreshed summary")
        assert place.period is None
        assert place.sources == ["Field visit (2026)"]
        assert place.photo_captions[gallery[0]] == "West façade at noon"
        assert place.gallery == list(gallery)


def test_admin_can_edit_any_place(app, admin_client):
    slug = _seeded_place(app)
    with app.app_context():
        gallery = HeritagePlace.query.filter_by(slug=slug).first().gallery
    resp = admin_client.post(
        f"/place/{slug}/edit",
        data={
            "title": "Admin Touched This One",
            "summary": "An administrator corrected the record details for accuracy.",
            "location": "Qusayr",
            "governorate": "Aswan",
            "category": "1",
            "keep_0": "on",
            "path_0": gallery[0],
            "terms": "on",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        place = HeritagePlace.query.filter_by(slug=slug).first()
        assert place.title == "Admin Touched This One"


def test_edit_rejects_removing_all_photos(app, client):
    slug = _seeded_place(app)
    owner = login_client(app, "mahmoud", SEED_PASSWORD)
    resp = owner.post(
        f"/place/{slug}/edit",
        data={
            "title": "No Photos Left",
            "summary": "Trying to remove every photo should be blocked by validation.",
            "location": "Qusayr",
            "governorate": "Aswan",
            "category": "1",
            "terms": "on",
        },
        follow_redirects=True,
    )
    body = resp.get_data(as_text=True)
    assert "at least one photo" in body
    with app.app_context():
        place = HeritagePlace.query.filter_by(slug=slug).first()
        assert place.gallery  # untouched
        assert place.title != "No Photos Left"


def test_edit_can_upload_new_captioned_photos(app, client):
    slug = _seeded_place(app)
    owner = login_client(app, "mahmoud", SEED_PASSWORD)
    with app.app_context():
        old_gallery = list(HeritagePlace.query.filter_by(slug=slug).first().gallery)

    resp = owner.post(
        f"/place/{slug}/edit",
        data={
            "title": "Deir al-Qusayr",
            "summary": "A summary long enough to satisfy the validation rules easily.",
            "location": "Qusayr",
            "governorate": "Aswan",
            "category": "1",
            "keep_0": "on",
            "path_0": old_gallery[0],
            "new_photos": [png_file("extra.png")],
            "photo_captions": ["Freshly uploaded detail shot"],
            "terms": "on",
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        place = HeritagePlace.query.filter_by(slug=slug).first()
        assert len(place.gallery) == 2
        new_paths = [p for p in place.gallery if p not in old_gallery]
        assert len(new_paths) == 1
        assert place.photo_captions[new_paths[0]] == "Freshly uploaded detail shot"
        assert place.photos == 2
