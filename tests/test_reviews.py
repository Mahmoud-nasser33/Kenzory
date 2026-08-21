"""Community ratings & reviews: posting, updating, deleting, aggregates."""

from kenzory.extensions import db
from kenzory.models import HeritagePlace, Review

from conftest import make_user_client


def _place(app):
    with app.app_context():
        place = HeritagePlace.query.filter_by(status="approved").first()
        db.session.expunge(place)
        return place.slug


def _aggregate(app, slug):
    with app.app_context():
        place = HeritagePlace.query.filter_by(slug=slug).first()
        return place.rating, place.rating_count


def test_anonymous_cannot_review(client):
    slug = _place(client.application)
    resp = client.post(f"/place/{slug}/review", data={"rating": "5"})
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_user_can_review_and_aggregate_updates(app, client):
    slug = _place(app)
    tester = make_user_client(app, "reviewer_a")

    before_count = _aggregate(app, slug)[1]
    resp = tester.post(
        f"/place/{slug}/review",
        data={"rating": "5", "body": "A wonderful hidden gem."},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "A wonderful hidden gem." in resp.get_data(as_text=True)

    rating, count = _aggregate(app, slug)
    assert count == before_count + 1

    # exact average check against the rows themselves
    with app.app_context():
        place = HeritagePlace.query.filter_by(slug=slug).first()
        reviews = Review.query.filter_by(place_id=place.id).all()
        avg = round(sum(r.rating for r in reviews) / len(reviews), 1)
        assert place.rating == avg
        assert place.rating_count == len(reviews)


def test_one_review_per_user_upserts(app, client):
    slug = _place(app)
    tester = make_user_client(app, "reviewer_b")

    tester.post(f"/place/{slug}/review", data={"rating": "4", "body": "First take."})
    tester.post(f"/place/{slug}/review", data={"rating": "2", "body": "Changed my mind."})

    with app.app_context():
        from kenzory.models import User

        uid = User.query.filter_by(username="reviewer_b").first().id
        rows = Review.query.filter_by(user_id=uid).all()
        assert len(rows) == 1
        assert rows[0].rating == 2
        assert rows[0].body == "Changed my mind."


def test_invalid_rating_rejected(app, client):
    slug = _place(app)
    tester = make_user_client(app, "reviewer_c")
    before = _aggregate(app, slug)[1]

    for bad in ("0", "6", "abc", ""):
        resp = tester.post(f"/place/{slug}/review", data={"rating": bad}, follow_redirects=True)
        assert "star rating" in resp.get_data(as_text=True)

    assert _aggregate(app, slug)[1] == before


def test_body_over_limit_rejected(app, client):
    slug = _place(app)
    tester = make_user_client(app, "reviewer_d")
    resp = tester.post(
        f"/place/{slug}/review",
        data={"rating": "4", "body": "x" * 1001},
        follow_redirects=True,
    )
    assert "limited to 1000 characters" in resp.get_data(as_text=True)
    with app.app_context():
        from kenzory.models import User

        uid = User.query.filter_by(username="reviewer_d").first().id
        assert Review.query.filter_by(user_id=uid).count() == 0


def test_delete_own_review(app, client):
    slug = _place(app)
    tester = make_user_client(app, "reviewer_e")
    tester.post(f"/place/{slug}/review", data={"rating": "3", "body": "Okay-ish."})
    assert _aggregate(app, slug)[1] >= 1

    resp = tester.post(f"/place/{slug}/review/delete", follow_redirects=True)
    assert "removed" in resp.get_data(as_text=True)

    with app.app_context():
        uid_query = Review.query.filter(Review.rating == 3, Review.body == "Okay-ish.").all()
        assert uid_query == []


def test_cannot_delete_someone_elses_review(app, client):
    slug = _place(app)
    owner = make_user_client(app, "review_owner")
    owner.post(f"/place/{slug}/review", data={"rating": "5", "body": "Mine."})

    other = make_user_client(app, "review_other")
    resp = other.post(f"/place/{slug}/review/delete", follow_redirects=True)
    assert "no review to remove" in resp.get_data(as_text=True)

    with app.app_context():
        assert Review.query.filter_by(body="Mine.").count() == 1


def test_reviews_sorted_newest_first(app, client):
    slug = _place(app)
    first = make_user_client(app, "rev_first")
    second = make_user_client(app, "rev_second")
    first.post(f"/place/{slug}/review", data={"rating": "5", "body": "Earlier review."})
    second.post(f"/place/{slug}/review", data={"rating": "4", "body": "Later review."})

    resp = second.get(f"/place/{slug}")
    body = resp.get_data(as_text=True)
    assert body.index("Later review.") < body.index("Earlier review.")


def test_place_page_shows_rating_summary(client):
    slug = _place(client.application)
    resp = client.get(f"/place/{slug}")
    assert resp.status_code == 200
    assert b"Ratings" in resp.data and b"reviews" in resp.data


def test_seeded_places_have_real_review_rows(app):
    """Every seeded rating must be backed by actual review rows."""
    with app.app_context():
        places = HeritagePlace.query.filter_by(status="approved").all()
        assert places, "seed should create places"
        for place in places:
            rows = Review.query.filter_by(place_id=place.id).count()
            if place.rating > 0:
                assert rows > 0, f"{place.slug} shows a rating with no reviews"
                assert place.rating_count == rows
