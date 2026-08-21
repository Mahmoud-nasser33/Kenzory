"""Review business logic: validation, upsert/delete, aggregate sync.

``HeritagePlace.rating`` and ``rating_count`` are denormalised aggregates
shown on cards and used for sorting; every write path funnels through here
so they stay consistent with the ``reviews`` table.
"""

from datetime import datetime

from sqlalchemy import func, select

from kenzory.extensions import db
from kenzory.models import MAX_BODY_LENGTH, MAX_RATING, MIN_RATING, HeritagePlace, Review


class ReviewValidationError(ValueError):
    """Raised with a user-facing message when a review payload is invalid."""


def validate_rating(raw):
    """Coerce ``raw`` to an int in [1, 5] or raise ReviewValidationError."""
    try:
        rating = int(str(raw).strip())
    except (TypeError, ValueError):
        raise ReviewValidationError("Please choose a star rating between 1 and 5.")
    if not MIN_RATING <= rating <= MAX_RATING:
        raise ReviewValidationError("Please choose a star rating between 1 and 5.")
    return rating


def validate_body(body):
    """Trimmed review text; may be empty but not over the length cap."""
    text = (body or "").strip()
    if len(text) > MAX_BODY_LENGTH:
        raise ReviewValidationError(
            f"Reviews are limited to {MAX_BODY_LENGTH} characters."
        )
    return text


def get_review(place_id, user_id):
    return db.session.scalar(
        select(Review).where(Review.place_id == place_id, Review.user_id == user_id)
    )


def upsert_review(place, user, rating, body):
    """Create or update the user's review of ``place``, then resync aggregates."""
    review = get_review(place.id, user.id)
    created = review is None
    if created:
        review = Review(place_id=place.id, user_id=user.id, created_at=datetime.utcnow())
        db.session.add(review)
    review.rating = rating
    review.body = body
    review.updated_at = datetime.utcnow()
    db.session.flush()
    recompute_rating(place)
    return review, created


def delete_review(review):
    """Remove a review and resync its place's aggregates."""
    place = review.place
    db.session.delete(review)
    db.session.flush()
    recompute_rating(place)


def recompute_rating(place):
    """Sync place.rating / rating_count with the real review rows."""
    count, avg = db.session.execute(
        select(func.count(Review.id), func.coalesce(func.avg(Review.rating), 0.0))
        .where(Review.place_id == place.id)
    ).one()
    place.rating_count = int(count)
    place.rating = round(float(avg), 1) if count else 0.0


def recompute_all_ratings():
    """Resync every place (used after seeding bulk review rows)."""
    for place in HeritagePlace.query.all():
        recompute_rating(place)


def place_reviews(place):
    """Newest-first reviews with their authors loaded."""
    return (
        Review.query.filter_by(place_id=place.id)
        .order_by(Review.created_at.desc(), Review.id.desc())
        .all()
    )


def rating_distribution(place):
    """{stars: count} for stars 5..1, for summary display."""
    rows = db.session.execute(
        select(Review.rating, func.count(Review.id))
        .where(Review.place_id == place.id)
        .group_by(Review.rating)
    ).all()
    counts = {stars: 0 for stars in range(MAX_RATING, 0, -1)}
    for stars, total in rows:
        counts[int(stars)] = int(total)
    return counts
