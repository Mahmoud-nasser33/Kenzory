"""Community ratings & reviews for heritage places."""

from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user

from kenzory.auth import login_required
from kenzory.extensions import db
from kenzory.models import HeritagePlace
from kenzory.services.reviews import (
    ReviewValidationError,
    delete_review as remove_review,
    get_review,
    upsert_review,
    validate_body,
    validate_rating,
)

reviews_bp = Blueprint("reviews", __name__)


def _approved_place_or_404(slug):
    return HeritagePlace.query.filter_by(slug=slug, status="approved").first_or_404()


def _redirect_to_reviews(slug):
    return redirect(url_for("places.place_detail", slug=slug) + "#reviews")


@reviews_bp.route("/place/<slug>/review", methods=["POST"])
@login_required
def submit_review(slug):
    place = _approved_place_or_404(slug)

    try:
        rating = validate_rating(request.form.get("rating"))
        body = validate_body(request.form.get("body"))
    except ReviewValidationError as exc:
        flash(str(exc), "error")
        return _redirect_to_reviews(slug)

    _, created = upsert_review(place, current_user, rating, body)
    db.session.commit()
    if created:
        flash("Thanks — your review has been posted.", "success")
    else:
        flash("Your review has been updated.", "success")
    return _redirect_to_reviews(slug)


@reviews_bp.route("/place/<slug>/review/delete", methods=["POST"])
@login_required
def delete_review(slug):
    place = _approved_place_or_404(slug)
    review = get_review(place.id, current_user.id)
    if review is None:
        flash("You have no review to remove on this place.", "info")
        return _redirect_to_reviews(slug)

    remove_review(review)
    db.session.commit()
    flash("Your review was removed.", "info")
    return _redirect_to_reviews(slug)
