"""Heritage place detail pages."""

from flask import Blueprint, render_template

from kenzory.models import HeritagePlace
from kenzory.services.places import place_images, place_image, related_places

places_bp = Blueprint("places", __name__)


@places_bp.route("/place/<slug>")
def place_detail(slug):
    place = (
        HeritagePlace.query.filter_by(slug=slug, status="approved").first_or_404()
    )
    return render_template(
        "place.html",
        place=place,
        related=related_places(place),
        gallery=place_images(place),
        place_image=place_image,
    )
