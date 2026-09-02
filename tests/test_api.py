"""Tests for the public REST API and radius (nearby) search."""

import pytest

from kenzory.models import HeritagePlace


def place_coords(client):
    """Return (lat, lng) of the first approved place via the API."""
    data = client.get("/api/places").get_json()
    p = data["places"][0]
    return p["latitude"], p["longitude"]


# ── Places API ──────────────────────────────────────────────────────

def test_places_list_pagination(client):
    data = client.get("/api/places").get_json()
    assert "places" in data and "pagination" in data
    assert data["pagination"]["total"] > 0
    assert 0 < len(data["places"]) <= data["pagination"]["per_page"]


def test_places_list_filter_by_category(client):
    data = client.get("/api/places?category=historical-sites").get_json()
    assert len(data["places"]) > 0
    for p in data["places"]:
        assert p["category"]["slug"] == "historical-sites"


def test_places_list_search(client):
    first = client.get("/api/places").get_json()["places"][0]
    term = first["title"].split()[0]
    data = client.get("/api/places", query_string={"q": term}).get_json()
    titles = [p["title"].lower() for p in data["places"]]
    assert any(term.lower() in t for t in titles)


def test_places_list_featured_flag(client):
    data = client.get("/api/places?featured=1&per_page=100").get_json()
    for p in data["places"]:
        assert p["featured"] is True


def test_get_place_by_slug(client):
    place = client.get("/api/places").get_json()["places"][0]
    data = client.get(f"/api/places/{place['slug']}").get_json()
    assert data["title"] == place["title"]
    assert "gallery" in data
    assert "latitude" in data


def test_get_place_by_id(client):
    place = client.get("/api/places").get_json()["places"][0]
    data = client.get(f"/api/places/{place['id']}").get_json()
    assert data["id"] == place["id"]


def test_get_place_missing(client):
    resp = client.get("/api/places/does-not-exist-xyz")
    assert resp.status_code == 404


# ── Stories API ─────────────────────────────────────────────────────

def test_stories_list(client):
    data = client.get("/api/stories").get_json()
    assert "stories" in data and data["pagination"]["total"] > 0


def test_get_story(client):
    story = client.get("/api/stories").get_json()["stories"][0]
    data = client.get(f"/api/stories/{story['slug']}").get_json()
    assert data["title"] == story["title"]


def test_get_story_missing(client):
    assert client.get("/api/stories/no-such-story").status_code == 404


# ── Categories API ──────────────────────────────────────────────────

def test_categories_list(client):
    data = client.get("/api/categories").get_json()
    assert len(data["categories"]) == 8
    for cat in data["categories"]:
        assert "place_count" in cat


# ── Stats API ───────────────────────────────────────────────────────

def test_stats(client):
    data = client.get("/api/stats").get_json()
    assert data["total_places"] > 0
    assert data["total_users"] > 0
    assert data["governorates_covered"] > 0


# ── Radius search ───────────────────────────────────────────────────

def test_nearby_returns_sorted_by_distance(client):
    lat, lng = place_coords(client)
    data = client.get("/api/nearby", query_string={
        "lat": lat, "lng": lng, "radius": 500, "sort": "distance",
    }).get_json()
    assert data["pagination"]["total"] > 0
    # center place should be first / closest
    distances = [p["distance_km"] for p in data["places"]]
    assert distances == sorted(distances)


def test_nearby_radius_limits(client):
    lat, lng = place_coords(client)
    small = client.get("/api/nearby", query_string={
        "lat": lat, "lng": lng, "radius": 0.001,
    }).get_json()
    large = client.get("/api/nearby", query_string={
        "lat": lat, "lng": lng, "radius": 500,
    }).get_json()
    # a tiny radius should return fewer (or equal) results than a huge one
    assert small["pagination"]["total"] <= large["pagination"]["total"]


def test_nearby_requires_lat_lng(client):
    assert client.get("/api/nearby").status_code == 400
    assert client.get("/api/nearby?lat=30&lng=abc").status_code == 400


def test_nearby_validates_range(client):
    assert client.get("/api/nearby?lat=200&lng=0").status_code == 400


def test_nearby_honors_governorate_filter(client, app):
    lat, lng = place_coords(client)
    with app.app_context():
        gov = HeritagePlace.query.filter_by(status="approved").first().governorate
    data = client.get("/api/nearby", query_string={
        "lat": lat, "lng": lng, "radius": 500, "governorate": gov,
    }).get_json()
    assert data["pagination"]["total"] > 0
    for p in data["places"]:
        assert p["governorate"] == gov
