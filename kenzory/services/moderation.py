"""Moderation logic: approving a submission publishes a HeritagePlace."""

from datetime import datetime

from kenzory.extensions import db
from kenzory.models import HeritagePlace, Submission, User
from kenzory.services.covers import ensure_cover
from kenzory.services.notifications import notify_submission_approved, notify_submission_rejected
from kenzory.services.security import slugify


def unique_slug(base, model=HeritagePlace):
    slug = slugify(base) or "place"
    candidate = slug
    n = 2
    while db.session.query(model.id).filter(model.slug == candidate).first():
        candidate = f"{slug}-{n}"
        n += 1
    return candidate


def approve_submission(submission, reviewer, note=None):
    """Approve a submission and create its published place record."""
    gallery = list(submission.images or [])
    image = gallery[0] if gallery else None
    if not image:
        image = ensure_cover(
            slugify(submission.title) or f"place-{submission.id}",
            submission.category.name if submission.category else "Hidden Gems",
            submission.title,
            submission.location,
        )

    place = HeritagePlace(
        slug=unique_slug(submission.title),
        title=submission.title,
        summary=submission.summary or "",
        description=submission.description or submission.summary or "",
        historical_background=submission.historical_information,
        location=submission.location,
        governorate=submission.governorate,
        latitude=submission.latitude,
        longitude=submission.longitude,
        category_id=submission.category_id,
        period=submission.period or "Not specified",
        image=image,
        gallery=gallery,
        photo_captions=dict(submission.image_captions or {}),
        sources=([submission.sources] if submission.sources else []),
        photos=len(gallery),
        status="approved",
        created_by=submission.submitted_by,
    )
    db.session.add(place)
    submission.status = "approved"
    submission.reviewer_id = reviewer.id
    submission.review_note = (note or "").strip() or None
    submission.reviewed_at = datetime.utcnow()

    submitter = db.session.get(User, submission.submitted_by)
    if submitter:
        notify_submission_approved(place, submitter)

    db.session.commit()
    return place


def reject_submission(submission, reviewer, note):
    submission.status = "rejected"
    submission.reviewer_id = reviewer.id
    submission.review_note = (note or "").strip() or None
    submission.reviewed_at = datetime.utcnow()

    notify_submission_rejected(submission, note)

    db.session.commit()
