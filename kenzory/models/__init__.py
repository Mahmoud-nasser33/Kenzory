"""Database models. Import them all here so `db.create_all()` and Alembic
autogenerate see every table."""

from kenzory.models.category import Category
from kenzory.models.place import (
    PUBLIC_STATUSES,
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REJECTED,
    HeritagePlace,
)
from kenzory.models.review import MAX_BODY_LENGTH, MAX_RATING, MIN_RATING, Review
from kenzory.models.story import Story
from kenzory.models.submission import (
    SUBMISSION_STATUSES,
    Submission,
)
from kenzory.models.user import ROLE_ADMIN, ROLE_USER, User
from kenzory.models.vote import SubmissionVote

__all__ = [
    "PUBLIC_STATUSES",
    "STATUS_APPROVED",
    "STATUS_PENDING",
    "STATUS_REJECTED",
    "SUBMISSION_STATUSES",
    "ROLE_ADMIN",
    "ROLE_USER",
    "MAX_BODY_LENGTH",
    "MAX_RATING",
    "MIN_RATING",
    "Category",
    "HeritagePlace",
    "Review",
    "Story",
    "Submission",
    "SubmissionVote",
    "User",
]
