"""Heritage place detail pages."""

from flask import Blueprint, render_template
from flask_login import current_user

from kenzory.models import HeritagePlace
from kenzory.services.places import gallery_items, place_image, related_places
from kenzory.services.reviews import get_review, place_reviews, rating_distribution

places_bp = Blueprint("places", __name__)


@places_bp.route("/place/<slug>")
def place_detail(slug):
    place = (
        HeritagePlace.query.filter_by(slug=slug, status="approved").first_or_404()
    )
    reviews = place_reviews(place)
    my_review = None
    if current_user.is_authenticated:
        my_review = get_review(place.id, current_user.id)
    return render_template(
        "place.html",
        place=place,
        related=related_places(place),
        gallery=gallery_items(place),
        place_image=place_image,
        reviews=reviews,
        my_review=my_review,
        distribution=rating_distribution(place),
    )
