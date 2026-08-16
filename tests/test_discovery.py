"""Public discovery pages: home, explore, place detail, map, stories."""

from kenzory.models import HeritagePlace


def test_home_shows_real_stats(app, client):
    resp = client.get("/")
    assert resp.status_code == 200
    with app.app_context():
        total = HeritagePlace.query.filter_by(status="approved").count()
    body = resp.get_data(as_text=True)
    assert str(total) in body
    assert "featured" in body or "places documented" in body


def test_home_lists_featured(app, client):
    resp = client.get("/")
    with app.app_context():
        featured = HeritagePlace.query.filter_by(featured=True, status="approved").first()
    if featured:
        assert featured.title in resp.get_data(as_text=True)


def test_explore_lists_all_approved(app, client):
    resp = client.get("/explore")
    assert resp.status_code == 200
    with app.app_context():
        total = HeritagePlace.query.filter_by(status="approved").count()
    assert str(total) in resp.get_data(as_text=True)


def test_explore_filters_by_governorate(app, client):
    with app.app_context():
        gov = HeritagePlace.query.filter_by(status="approved").first().governorate
    resp = client.get(f"/explore?governorate={gov}")
    assert resp.status_code == 200
    assert gov in resp.get_data(as_text=True)


def test_explore_search_query(app, client):
    with app.app_context():
        title = HeritagePlace.query.filter_by(status="approved").first().title
    term = title.split()[0]
    resp = client.get(f"/explore?q={term}")
    assert resp.status_code == 200
    assert title in resp.get_data(as_text=True)


def test_explore_sort_options(app, client):
    for sort in ("featured", "rating", "saves", "newest", "name"):
        resp = client.get(f"/explore?sort={sort}")
        assert resp.status_code == 200


def test_place_detail_approved(client):
    from kenzory.models import HeritagePlace

    with client.application.app_context():
        place = HeritagePlace.query.filter_by(status="approved").first()
        slug = place.slug
    resp = client.get(f"/place/{slug}")
    assert resp.status_code == 200
    assert place.title in resp.get_data(as_text=True)


def test_place_detail_unknown_slug(client):
    assert client.get("/place/does-not-exist").status_code == 404


def test_map_page_serializes_places(client):
    resp = client.get("/map")
    assert resp.status_code == 200
    assert b"PLACES_JSON" in resp.data


def test_stories_index(client):
    resp = client.get("/stories")
    assert resp.status_code == 200


def test_story_detail(client):
    from kenzory.models import Story

    with client.application.app_context():
        story = Story.query.first()
    if story:
        resp = client.get(f"/stories/{story.slug}")
        assert resp.status_code == 200
        assert story.title in resp.get_data(as_text=True)


def test_about_uses_real_numbers(client):
    resp = client.get("/about")
    body = resp.get_data(as_text=True)
    assert "Documented places" in body
    assert "1,284" not in body


def test_discoveries_feed(client):
    assert client.get("/discoveries").status_code == 200


def test_error_page_renders(client):
    assert client.get("/missing-page-xyz").status_code == 404
    assert b"404" in client.get("/missing-page-xyz").data
