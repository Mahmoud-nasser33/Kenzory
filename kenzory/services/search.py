"""Explore search and filtering.

All filtering, sorting and pagination happens in the database. The browser
never receives the full table — it only ever gets one page of results.
"""

import math

from flask import current_app
from sqlalchemy import or_, select

from kenzory.extensions import db
from kenzory.models import Category, HeritagePlace

_SORTS = {
    "featured": (HeritagePlace.featured.desc(), HeritagePlace.rating.desc()),
    "rating": (HeritagePlace.rating.desc(),),
    "saves": (HeritagePlace.saves.desc(),),
    "newest": (HeritagePlace.created_at.desc(),),
    "name": (HeritagePlace.title.asc(),),
    "distance": None,  # handled separately after query
}


def _text_terms(text):
    return [t for t in text.split() if t.strip()]


def haversine_km(lat1, lon1, lat2, lon2):
    """Return the great-circle distance in km between two points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def query_places(q="", category=None, governorate=None, period=None, sort="featured"):
    query = select(HeritagePlace).where(HeritagePlace.status == "approved")

    if q:
        terms = _text_terms(q)
        if terms:
            like = lambda column: [column.ilike(f"%{term}%") for term in terms]
            query = query.where(
                or_(
                    *like(HeritagePlace.title),
                    *like(HeritagePlace.summary),
                    *like(HeritagePlace.description),
                    *like(HeritagePlace.location),
                    *like(HeritagePlace.governorate),
                    *like(HeritagePlace.region),
                    *like(HeritagePlace.period),
                )
            )

    if category:
        cat = db.session.scalar(
            select(Category).where(
                or_(Category.slug == category, Category.name == category)
            )
        )
        if cat:
            query = query.where(HeritagePlace.category_id == cat.id)

    if governorate:
        query = query.where(HeritagePlace.governorate == governorate)

    if period:
        query = query.where(HeritagePlace.period == period)

    order = _SORTS.get(sort, _SORTS["featured"])
    if order is not None:
        query = query.order_by(*order)
    return query


def paginate_places(q="", category=None, governorate=None, period=None, sort="featured", page=1):
    query = query_places(
        q=q, category=category, governorate=governorate, period=period, sort=sort
    )
    return db.paginate(
        query, page=page, per_page=current_app.config["PER_PAGE"], error_out=False
    )


def radius_search(lat, lng, radius_km=50, q="", category=None, governorate=None,
                   period=None, sort="featured", page=1, per_page=20):
    """Find approved places within ``radius_km`` of (lat, lng).

    Returns a dict with ``items`` (list of HeritagePlace with attached
    ``.distance_km`` attribute), ``total`` count, and ``page`` / ``pages``.
    """
    base_query = query_places(q=q, category=category, governorate=governorate,
                               period=period, sort=sort)
    base_query = base_query.where(
        HeritagePlace.latitude.isnot(None),
        HeritagePlace.longitude.isnot(None),
    )

    all_places = db.session.scalars(base_query).all()

    nearby = []
    for place in all_places:
        dist = haversine_km(lat, lng, place.latitude, place.longitude)
        if dist <= radius_km:
            place.distance_km = round(dist, 2)
            nearby.append(place)

    if sort == "distance":
        nearby.sort(key=lambda p: p.distance_km)
    elif _SORTS.get(sort):
        pass  # already ordered by DB sort

    total = len(nearby)
    start = (page - 1) * per_page
    items = nearby[start:start + per_page]
    pages = math.ceil(total / per_page) if per_page else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages,
        "per_page": per_page,
    }


def category_counts():
    """Approved place counts keyed by category slug, for Explore chips."""
    rows = db.session.execute(
        select(Category.slug, db.func.count(HeritagePlace.id))
        .join(HeritagePlace, HeritagePlace.category_id == Category.id)
        .where(HeritagePlace.status == "approved")
        .group_by(Category.slug)
    ).all()
    return {slug: total for slug, total in rows}
