"""User profile."""

from flask import Blueprint, render_template
from flask_login import current_user

from kenzory.auth import login_required
from kenzory.models import HeritagePlace, Submission

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    places = (
        HeritagePlace.query.filter_by(created_by=current_user.id)
        .order_by(HeritagePlace.created_at.desc())
        .all()
    )
    submissions = (
        Submission.query.filter_by(submitted_by=current_user.id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    pending = sum(1 for s in submissions if s.status == "pending")
    approved = sum(1 for s in submissions if s.status == "approved")
    rejected = sum(1 for s in submissions if s.status == "rejected")
    return render_template(
        "profile.html",
        places=places,
        submissions=submissions,
        counts={"pending": pending, "approved": approved, "rejected": rejected},
    )
