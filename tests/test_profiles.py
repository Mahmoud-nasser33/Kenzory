"""Tests for community profiles — own profile and public contributor pages."""

from kenzory.extensions import db
from kenzory.models import HeritagePlace, Review, Submission, User
from kenzory.services.profile import (
    compute_level,
    compute_reputation,
    earn_badges,
    get_profile_data,
    LEVELS,
)


# ---------------------------------------------------------------------------
# Service-level unit tests
# ---------------------------------------------------------------------------

class TestReputation:
    def test_zero_reputation_new_user(self, app):
        with app.app_context():
            user = User(username="blank", email="blank@test.com", display_name="Blank")
            user.set_password("x")
            db.session.add(user)
            db.session.flush()
            total, parts = compute_reputation(user)
            assert total == 0
            assert all(p["value"] == 0 for p in parts)

    def test_reputation_increases_with_places(self, app, admin_client):
        with app.app_context():
            user = User.query.filter_by(username="mahmoud").first()
            total, parts = compute_reputation(user)
            assert total > 0
            assert any(p["label"] == "Verified records" and p["value"] > 0 for p in parts)


class TestLevel:
    def test_level_newcomer_at_zero(self):
        assert compute_level(0) == "Newcomer"

    def test_level_contributor_at_100(self):
        assert compute_level(100) == "Contributor"

    def test_level_progresses(self):
        assert compute_level(300) == "Explorer"
        assert compute_level(600) == "Heritage Guide"
        assert compute_level(1200) == "Senior Guide"
        assert compute_level(2500) == "Heritage Guardian"

    def test_level_highest_at_high_rep(self):
        assert compute_level(5000) == "Heritage Guardian"


class TestBadges:
    def test_new_user_no_badges(self, app):
        with app.app_context():
            user = User(username="newbie", email="newbie@test.com", display_name="Newbie")
            user.set_password("x")
            db.session.add(user)
            db.session.flush()
            badges = earn_badges(user, 0)
            assert all(not b["earned"] for b in badges)

    def test_seeded_user_has_badges(self, app):
        with app.app_context():
            user = User.query.filter_by(username="mahmoud").first()
            badges = earn_badges(user, 0)
            earned = [b["id"] for b in badges if b["earned"]]
            assert "first" in earned


class TestGetProfileData:
    def test_returns_expected_keys(self, app):
        with app.app_context():
            user = User.query.filter_by(username="mahmoud").first()
            data = get_profile_data(user)
            expected_keys = {
                "user", "places", "submissions", "counts",
                "reputation", "reputation_parts", "level", "badges",
                "photos", "place_count", "review_count", "endorsement_count",
            }
            assert expected_keys == set(data.keys())


# ---------------------------------------------------------------------------
# Route-level integration tests
# ---------------------------------------------------------------------------

class TestProfileRoute:
    def test_profile_requires_login(self, client):
        resp = client.get("/profile")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_profile_page_renders(self, client):
        from tests.conftest import login_client
        user_client = login_client(client.application, "mahmoud", "Kenzory123!")
        resp = user_client.get("/profile")
        assert resp.status_code == 200
        assert b"mahmoud" in resp.data

    def test_profile_shows_badges(self, client):
        from tests.conftest import login_client
        user_client = login_client(client.application, "mahmoud", "Kenzory123!")
        resp = user_client.get("/profile")
        assert b"Badges" in resp.data
        assert b"First Discovery" in resp.data

    def test_profile_shows_reputation(self, client):
        from tests.conftest import login_client
        user_client = login_client(client.application, "mahmoud", "Kenzory123!")
        resp = user_client.get("/profile")
        assert b"Reputation" in resp.data
        assert b"points" in resp.data or b"Verified records" in resp.data

    def test_profile_shows_level(self, client):
        from tests.conftest import login_client
        user_client = login_client(client.application, "mahmoud", "Kenzory123!")
        resp = user_client.get("/profile")
        assert b"Newcomer" in resp.data or b"Contributor" in resp.data or b"Explorer" in resp.data or b"Heritage Guide" in resp.data or b"Senior Guide" in resp.data or b"Heritage Guardian" in resp.data

    def test_profile_shows_bio(self, client):
        from tests.conftest import login_client
        user_client = login_client(client.application, "mahmoud", "Kenzory123!")
        resp = user_client.get("/profile")
        assert b"profile-bio" in resp.data

    def test_profile_shows_places(self, client):
        from tests.conftest import login_client
        user_client = login_client(client.application, "mahmoud", "Kenzory123!")
        resp = user_client.get("/profile")
        assert resp.status_code == 200
        assert b"Places you" in resp.data


class TestContributorRoute:
    def test_contributor_page_renders(self, client):
        resp = client.get("/contributor/mahmoud")
        assert resp.status_code == 200
        assert b"mahmoud" in resp.data
        assert b"Heritage places by" in resp.data

    def test_contributor_shows_badges(self, client):
        resp = client.get("/contributor/mahmoud")
        assert b"Badges" in resp.data
        assert b"First Discovery" in resp.data

    def test_contributor_shows_level(self, client):
        resp = client.get("/contributor/mahmoud")
        assert b"Newcomer" in resp.data or b"Contributor" in resp.data or b"Explorer" in resp.data or b"Heritage Guide" in resp.data or b"Senior Guide" in resp.data or b"Heritage Guardian" in resp.data

    def test_contributor_shows_reputation(self, client):
        resp = client.get("/contributor/mahmoud")
        assert b"Reputation" in resp.data

    def test_contributor_404_for_unknown(self, client):
        resp = client.get("/contributor/nonexistent-user")
        assert resp.status_code == 404

    def test_contributor_no_submissions_section(self, client):
        resp = client.get("/contributor/mahmoud")
        assert b"Submissions" not in resp.data

    def test_contributor_link_on_place_detail(self, client):
        resp = client.get("/place/deir-al-qusayr")
        assert resp.status_code == 200
        assert b"/contributor/mahmoud" in resp.data


class TestBioAndLevel:
    def test_user_model_has_bio_field(self, app):
        with app.app_context():
            user = User.query.filter_by(username="mahmoud").first()
            assert hasattr(user, "bio")
            assert isinstance(user.bio, str)

    def test_user_model_has_level_field(self, app):
        with app.app_context():
            user = User.query.filter_by(username="mahmoud").first()
            assert hasattr(user, "level")
            assert isinstance(user.level, str)

    def test_seeded_users_have_bios(self, app):
        with app.app_context():
            users = User.query.filter(User.username != "admin").all()
            for u in users:
                assert u.bio is not None

    def test_seeded_users_have_levels(self, app):
        with app.app_context():
            users = User.query.filter(User.username != "admin").all()
            for u in users:
                assert u.level in {l[1] for l in LEVELS}

    def test_admin_has_level(self, app):
        with app.app_context():
            admin = User.query.filter_by(username="admin").first()
            assert admin.level == "Heritage Guardian"
