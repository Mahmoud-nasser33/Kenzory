"""Helpers for rendering places: image URLs, JSON serialization, related."""

import json
import os

from flask import current_app, url_for

from kenzory.services.security import slugify


def _static_file_exists(rel_path):
    base = current_app.static_folder
    return bool(rel_path) and os.path.isfile(os.path.join(base, rel_path.replace("/", os.sep)))


def place_image(place):
    """Absolute URL for a place's cover image (photo or generated SVG)."""
    if _static_file_exists(place.image or ""):
        return url_for("static", filename=place.image)
    cover = f"img/covers/{slugify(place.slug) or 'place'}.svg"
    return url_for("static", filename=cover)


def place_images(place):
    """List of absolute URLs for a place's gallery."""
    return [url_for("static", filename=path) for path in place.gallery if path]


def place_json(place):
    return {
        "id": place.slug,
        "name": place.title,
        "nameAr": place.title_ar or "",
        "category": place.category.name if place.category else "",
        "governorate": place.governorate,
        "region": place.region or "",
        "period": place.period or "",
        "city": place.location,
        "lat": place.latitude or 0,
        "lng": place.longitude or 0,
        "image": place_image(place),
        "summary": place.summary,
        "rating": place.rating or 0,
        "ratingCount": place.rating_count or 0,
        "saves": place.saves or 0,
        "photos": place.photos or 0,
        "verified": place.verified,
        "featured": place.featured,
        "popular": place.popular,
        "visitMinutes": place.visit_minutes or 60,
        "distanceKm": place.distance_km or 0,
    }


def places_json(places):
    return json.dumps([place_json(p) for p in places], ensure_ascii=False)


def story_image(story):
    if _static_file_exists(story.image or ""):
        return url_for("static", filename=story.image)
    if story.place:
        return place_image(story.place)
    return url_for("static", filename="img/covers/deir-al-qusayr.svg")


def related_places(place, limit=3):
    """Places sharing a category or governorate, ranked by closeness."""
    from kenzory.models import HeritagePlace

    candidates = HeritagePlace.query.filter(
        HeritagePlace.status == "approved",
        HeritagePlace.id != place.id,
    ).all()
    scored = []
    for p in candidates:
        score = 0
        if p.category_id == place.category_id:
            score += 2
        if p.governorate == place.governorate:
            score += 2
        if p.period and p.period == place.period:
            score += 1
        scored.append((score, p))
    scored.sort(key=lambda x: (-x[0], -(x[1].saves or 0)))
    return [p for _, p in scored][:limit]
