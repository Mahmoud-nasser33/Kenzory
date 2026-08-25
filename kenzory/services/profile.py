"""Profile service — badges, reputation, and activity stats for contributors."""

from kenzory.extensions import db
from kenzory.models.place import HeritagePlace, STATUS_APPROVED
from kenzory.models.review import Review
from kenzory.models.submission import Submission
from kenzory.models.vote import SubmissionVote


# ---------------------------------------------------------------------------
# Badge definitions
# ---------------------------------------------------------------------------

BADGE_DEFS = [
    {
        "id": "first",
        "name": "First Discovery",
        "description": "Documented your first heritage place",
        "icon": "map-pin",
    },
    {
        "id": "five_places",
        "name": "Heritage Mapper",
        "description": "Documented five heritage places",
        "icon": "landmark",
    },
    {
        "id": "reviewer",
        "name": "Community Reviewer",
        "description": "Left your first review on a heritage place",
        "icon": "message-circle",
    },
    {
        "id": "ten_reviews",
        "name": "Trusted Voice",
        "description": "Left ten or more reviews",
        "icon": "star",
    },
    {
        "id": "endorser",
        "name": "Community Supporter",
        "description": "Endorsed a fellow contributor's submission",
        "icon": "thumbs-up",
    },
    {
        "id": "explorer",
        "name": "Heritage Explorer",
        "description": "Approved places span three or more governorates",
        "icon": "compass",
    },
    {
        "id": "storyteller",
        "name": "Storyteller",
        "description": "Your name appears as author on a published story",
        "icon": "book-open",
    },
    {
        "id": "guide",
        "name": "Local Guide",
        "description": "Ten or more approved heritage places",
        "icon": "award",
    },
]

# Reputation point values
REPUTATION_PER_APPROVED_PLACE = 50
REPUTATION_PER_REVIEW = 15
REPUTATION_PER_ENDORSEMENT = 5
REPUTATION_PER_PHOTO = 10

# Level thresholds (cumulative reputation)
LEVELS = [
    (0, "Newcomer"),
    (50, "Contributor"),
    (150, "Photographer"),
    (300, "Explorer"),
    (600, "Heritage Guide"),
    (1200, "Senior Guide"),
    (2500, "Heritage Guardian"),
]


def compute_reputation(user):
    """Compute total reputation and its breakdown for a user."""
    approved = HeritagePlace.query.filter_by(
        created_by=user.id, status=STATUS_APPROVED
    ).all()

    photos = sum(p.photos or 0 for p in approved)
    review_count = Review.query.filter_by(user_id=user.id).count()
    endorsement_count = SubmissionVote.query.filter_by(user_id=user.id).count()

    place_pts = len(approved) * REPUTATION_PER_APPROVED_PLACE
    review_pts = review_count * REPUTATION_PER_REVIEW
    endorse_pts = endorsement_count * REPUTATION_PER_ENDORSEMENT
    photo_pts = photos * REPUTATION_PER_PHOTO

    total = place_pts + review_pts + endorse_pts + photo_pts
    parts = [
        {"label": "Verified records", "value": place_pts},
        {"label": "Reviews", "value": review_pts},
        {"label": "Endorsements", "value": endorse_pts},
        {"label": "Photos", "value": photo_pts},
    ]
    return total, parts


def compute_level(reputation):
    """Derive level label from reputation score."""
    level = LEVELS[0][1]
    for threshold, name in LEVELS:
        if reputation >= threshold:
            level = name
    return level


def earn_badges(user, reputation):
    """Determine which badges a user has earned."""
    approved_count = HeritagePlace.query.filter_by(
        created_by=user.id, status=STATUS_APPROVED
    ).count()

    review_count = Review.query.filter_by(user_id=user.id).count()
    endorsement_count = SubmissionVote.query.filter_by(user_id=user.id).count()

    governorates = set(
        row[0]
        for row in db.session.query(HeritagePlace.governorate)
        .filter_by(created_by=user.id, status=STATUS_APPROVED)
        .distinct()
        .all()
    )

    from kenzory.models.story import Story

    has_story = Story.query.filter(
        Story.author.ilike(user.display_name)
    ).first() is not None

    earned = set()
    if approved_count >= 1:
        earned.add("first")
    if approved_count >= 5:
        earned.add("five_places")
    if review_count >= 1:
        earned.add("reviewer")
    if review_count >= 10:
        earned.add("ten_reviews")
    if endorsement_count >= 1:
        earned.add("endorser")
    if len(governorates) >= 3:
        earned.add("explorer")
    if has_story:
        earned.add("storyteller")
    if approved_count >= 10:
        earned.add("guide")

    return [
        {**b, "earned": b["id"] in earned}
        for b in BADGE_DEFS
    ]


def get_profile_data(user):
    """Return the full profile data dict for a user."""
    approved_places = (
        HeritagePlace.query.filter_by(created_by=user.id, status=STATUS_APPROVED)
        .order_by(HeritagePlace.created_at.desc())
        .all()
    )

    submissions = (
        Submission.query.filter_by(submitted_by=user.id)
        .order_by(Submission.created_at.desc())
        .all()
    )

    pending = sum(1 for s in submissions if s.status == "pending")
    approved = sum(1 for s in submissions if s.status == "approved")
    rejected = sum(1 for s in submissions if s.status == "rejected")

    reputation, reputation_parts = compute_reputation(user)
    level = compute_level(reputation)
    badges = earn_badges(user, reputation)

    photos = sum(p.photos or 0 for p in approved_places)

    return {
        "user": user,
        "places": approved_places,
        "submissions": submissions,
        "counts": {"pending": pending, "approved": approved, "rejected": rejected},
        "reputation": reputation,
        "reputation_parts": reputation_parts,
        "level": level,
        "badges": badges,
        "photos": photos,
        "place_count": len(approved_places),
        "review_count": user.review_count,
        "endorsement_count": user.endorsement_count,
    }
