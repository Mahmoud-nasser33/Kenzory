"""Trail helpers: slug generation, stop resolution, image + picker JSON."""

from flask import url_for

from kenzory.extensions import db
from kenzory.models import HeritagePlace, Trail, TrailStop
from kenzory.services.covers import ensure_cover
from kenzory.services.places import place_image
from kenzory.services.security import slugify

MIN_SUMMARY_LENGTH = 20


def unique_trail_slug(base):
    slug = slugify(base) or "trail"
    candidate = slug
    n = 2
    while (
        db.session.query(Trail.id).filter(Trail.slug == candidate).first()
    ):
        candidate = f"{slug}-{n}"
        n += 1
    return candidate


def resolve_stops(place_ids):
    """Resolve submitted place ids into approved places, preserving order.

    Returns a list of HeritagePlace in the order given. Unknown ids and places
    that are not approved are silently skipped; duplicates are dropped.
    """
    ordered = []
    seen = set()
    for raw in place_ids:
        try:
            place_id = int(raw)
        except (TypeError, ValueError):
            continue
        if place_id in seen:
            continue
        place = db.session.get(HeritagePlace, place_id)
        if place and place.status == "approved":
            seen.add(place_id)
            ordered.append(place)
    return ordered


def build_stops(trail, places):
    """Replace a trail's stops with the given ordered place list.

    The old rows are removed and flushed before the new ones are inserted so
    the (trail_id, place_id) unique constraint never sees both generations in
    the same unit of work.
    """
    trail.stops.clear()
    db.session.flush()
    for index, place in enumerate(places):
        trail.stops.append(
            TrailStop(trail_id=trail.id, place_id=place.id, position=index)
        )
    return trail.stops


def trail_image(trail):
    """Cover for a trail: its first place's image, or a generated cover."""
    first = trail.first_place
    if first:
        return url_for("static", filename=first.image) if first.image else _fallback_cover(trail)
    return _fallback_cover(trail)


def _fallback_cover(trail):
    cover = f"img/covers/{slugify(trail.slug) or 'trail'}.svg"
    return url_for("static", filename=cover)


def ensure_trail_cover(trail):
    """Write a cover SVG for a trail that has no image from its stops."""
    first = trail.first_place
    if first and first.image:
        trail.image = first.image
        return trail.image
    trail.image = ensure_cover(
        trail.slug,
        "Hidden Gems",
        trail.title,
        "",
    )
    return trail.image


def picker_json(places):
    """JSON payload for the trail stop picker (numeric ids for submission)."""
    return [
        {
            "dbId": p.id,
            "slug": p.slug,
            "name": p.title.split(" — ")[0],
            "summary": p.summary,
            "governorate": p.governorate,
            "image": place_image(p),
        }
        for p in places
    ]