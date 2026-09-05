"""Heritage trails: create/edit/delete, permissions, ordering, API."""

from kenzory.extensions import db
from kenzory.models import HeritagePlace, Trail

from conftest import make_user_client


def _approved_ids(app, count=3):
    with app.app_context():
        ids = [
            p.id
            for p in HeritagePlace.query.filter_by(status="approved")
            .order_by(HeritagePlace.id)
            .limit(count)
            .all()
        ]
        return ids


def _submit(client, path, title, summary, stop_ids, description=""):
    return client.post(
        path,
        data={
            "title": title,
            "summary": summary,
            "description": description,
            "place_ids": ",".join(str(i) for i in stop_ids),
        },
        follow_redirects=True,
    )


def _trail_slug(app, title):
    with app.app_context():
        trail = Trail.query.filter_by(title=title).first()
        return trail.slug if trail else None


# ---------------------------------------------------------------------------
# Browse + API
# ---------------------------------------------------------------------------


def test_anonymous_can_browse_trails(client):
    resp = client.get("/trails")
    assert resp.status_code == 200
    with client.application.app_context():
        assert Trail.query.count() >= 3


def test_trail_index_search(client):
    resp = client.get("/trails?q=desert")
    assert resp.status_code == 200
    assert b"desert" in resp.data.lower()


def test_trail_detail_shows_ordered_stops(client):
    with client.application.app_context():
        trail = Trail.query.first()
        slug = trail.slug
        stop_names = [s.place.title for s in trail.stops]
    resp = client.get(f"/trails/{slug}")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    for name in stop_names[:2]:
        assert name in body


def test_api_lists_trails(client):
    resp = client.get("/api/trails")
    assert resp.status_code == 200
    data = resp.get_json()
    with client.application.app_context():
        count = Trail.query.count()
    assert len(data["trails"]) == count
    assert data["pagination"]["total"] == count
    first = data["trails"][0]
    assert {"slug", "title", "stop_count", "total_minutes"} <= set(first)
    assert first["stop_count"] >= 2


def test_api_trail_detail_orders_stops(client):
    with client.application.app_context():
        trail = Trail.query.first()
        slug, expected = trail.slug, [s.place_id for s in trail.stops]
    resp = client.get(f"/api/trails/{slug}")
    assert resp.status_code == 200
    stops = [s["place"]["id"] for s in resp.get_json()["stops"]]
    assert stops == expected


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def test_anonymous_cannot_create_trail(client):
    resp = client.get("/trails/new")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_user_creates_trail_and_it_goes_live(app, client):
    ids = _approved_ids(app)
    assert len(ids) >= 2
    tester = make_user_client(app, "trail_creator")

    resp = _submit(tester, "/trails/new", "Gates of the Morning", "A walk through the old city gates at first light, past the bazaar.", ids)
    assert resp.status_code == 200
    assert "is live" in resp.get_data(as_text=True)

    with app.app_context():
        trail = Trail.query.filter_by(title="Gates of the Morning").first()
        assert trail is not None
        assert [s.place_id for s in trail.stops] == ids
        assert trail.total_minutes == sum((p.visit_minutes or 60) for p in trail.places)

    # public browse + detail + API all expose it
    assert client.get("/trails").status_code == 200
    detail = client.get(f"/trails/{trail.slug}")
    assert detail.status_code == 200
    api = client.get(f"/api/trails/{trail.slug}").get_json()
    assert api["slug"] == trail.slug


def test_trail_requires_minimum_stops(app, client):
    ids = _approved_ids(app, 1)
    tester = make_user_client(app, "trail_too_short")
    resp = _submit(tester, "/trails/new", "Too Short a Route", "One stop can hardly be called a trail, so this should fail validation.", ids)
    assert "at least 2 places" in resp.get_data(as_text=True)
    with app.app_context():
        assert Trail.query.filter_by(title="Too Short a Route").count() == 0


def test_duplicate_trail_titles_get_unique_slugs(app, client):
    ids = _approved_ids(app)
    tester = make_user_client(app, "trail_slug_a")
    _submit(tester, "/trails/new", "Same Name Trail", "A first route that shares its name with a later one, to test slugging.", ids)
    _submit(tester, "/trails/new", "Same Name Trail", "A second route with the same name, which must receive a numbered slug.", ids)
    with app.app_context():
        slugs = [t.slug for t in Trail.query.filter(Trail.title == "Same Name Trail").all()]
        assert len(slugs) == 2
        assert len(set(slugs)) == 2


# ---------------------------------------------------------------------------
# Edit / delete permissions
# ---------------------------------------------------------------------------


def test_non_creator_cannot_edit_or_delete(app, client):
    ids = _approved_ids(app)
    owner = make_user_client(app, "trail_owner_x")
    _submit(owner, "/trails/new", "Private Riverside Route", "A route along the river gardens that only its creator may manage.", ids)
    slug = _trail_slug(app, "Private Riverside Route")

    intruder = make_user_client(app, "trail_intruder")
    assert intruder.post(f"/trails/{slug}/edit", data={"title": "Hijacked"}).status_code == 403
    assert intruder.post(f"/trails/{slug}/delete").status_code == 403

    with app.app_context():
        assert Trail.query.filter_by(slug=slug).count() == 1


def test_creator_can_edit_their_trail(app, client):
    ids = _approved_ids(app)
    owner = make_user_client(app, "trail_editor")
    _submit(owner, "/trails/new", "Editable Loop", "A pleasant loop through the gardens and along the canal, all in one morning.", ids)
    slug = _trail_slug(app, "Editable Loop")

    resp = _submit(owner, f"/trails/{slug}/edit", "Editable Loop V2", "An updated description of the same loop, now with an evening leg.", ids)
    assert resp.status_code == 200
    assert "updated" in resp.get_data(as_text=True)
    with app.app_context():
        assert Trail.query.filter_by(slug=slug).first().title == "Editable Loop V2"


def test_creator_and_admin_can_delete(app, client):
    ids = _approved_ids(app)
    owner = make_user_client(app, "trail_deleter")
    _submit(owner, "/trails/new", "Doomed Trek", "A short arc budget for deletion experiments across each role.", ids)
    slug = _trail_slug(app, "Doomed Trek")

    resp = owner.post(f"/trails/{slug}/delete", follow_redirects=True)
    assert resp.status_code == 200
    assert "deleted" in resp.get_data(as_text=True)
    with app.app_context():
        assert Trail.query.filter_by(slug=slug).count() == 0


def test_admin_can_delete_someone_elses_trail(app, admin_client):
    ids = _approved_ids(app)
    owner = make_user_client(app, "trail_owner_y")
    _submit(owner, "/trails/new", "Admin Removal Target", "A route that only an administrator may remove on policy grounds.", ids)
    slug = _trail_slug(app, "Admin Removal Target")

    resp = admin_client.post(f"/trails/{slug}/delete", follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        assert Trail.query.filter_by(slug=slug).count() == 0