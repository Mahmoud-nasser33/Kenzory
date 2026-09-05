"""REST API — JSON endpoints for places, stories, categories and search.

All endpoints are public (read-only) and return ``application/json``.
Pagination follows the ``?page=N&per_page=N`` convention (default 20, max 100).
"""

import json
import math

from flask import Blueprint, jsonify, request
from sqlalchemy import func, select

from kenzory.extensions import db
from kenzory.models import Category, HeritagePlace, Story, Trail, User
from kenzory.services.places import gallery_items, place_image, story_image
from kenzory.services.search import query_places, radius_search
from kenzory.services.trails import trail_image


api_bp = Blueprint("api", __name__, url_prefix="/api")

PER_PAGE_DEFAULT = 20
PER_PAGE_MAX = 100


def _paginate_args():
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = min(max(int(request.args.get("per_page", PER_PAGE_DEFAULT)), 1), PER_PAGE_MAX)
    except (TypeError, ValueError):
        per_page = PER_PAGE_DEFAULT
    return page, per_page


def _pagination_meta(pagination):
    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


def _place_to_dict(place):
    return {
        "id": place.id,
        "slug": place.slug,
        "title": place.title,
        "summary": place.summary,
        "description": place.description,
        "historical_background": place.historical_background or "",
        "location": place.location,
        "region": place.region or "",
        "governorate": place.governorate,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "category": {
            "id": place.category.id,
            "name": place.category.name,
            "slug": place.category.slug,
            "icon": place.category.icon,
        } if place.category else None,
        "period": place.period or "",
        "approx_date": place.approx_date or "",
        "image": place_image(place),
        "key_facts": place.key_facts or [],
        "timeline": place.timeline or [],
        "architecture": place.architecture or [],
        "local_stories": place.local_stories or [],
        "sources": place.sources or [],
        "rating": place.rating or 0,
        "rating_count": place.rating_count or 0,
        "saves": place.saves or 0,
        "photos": place.photos or 0,
        "visit_minutes": place.visit_minutes or 60,
        "verified": place.verified,
        "featured": place.featured,
        "popular": place.popular,
        "created_at": place.created_at.isoformat() if place.created_at else None,
        "updated_at": place.updated_at.isoformat() if place.updated_at else None,
    }


def _story_to_dict(story):
    return {
        "id": story.id,
        "slug": story.slug,
        "title": story.title,
        "excerpt": story.excerpt,
        "author": story.author,
        "role": story.role or "",
        "read_minutes": story.read_minutes,
        "date": story.date or "",
        "image": story_image(story),
        "governorate": story.governorate or "",
        "category": story.category or "",
        "content": story.content or [],
        "place_id": story.place_id,
        "created_at": story.created_at.isoformat() if story.created_at else None,
    }


def _category_to_dict(cat, place_count=0):
    return {
        "id": cat.id,
        "name": cat.name,
        "slug": cat.slug,
        "description": cat.description or "",
        "icon": cat.icon,
        "tone": cat.tone,
        "place_count": place_count,
    }


def _trail_stop_to_dict(stop):
    place = stop.place
    return {
        "order": stop.position,
        "place": {
            "id": place.id,
            "slug": place.slug,
            "title": place.title,
            "summary": place.summary,
            "governorate": place.governorate,
            "location": place.location,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "category": place.category.name if place.category else "",
            "image": place_image(place),
            "visit_minutes": place.visit_minutes or 60,
        },
    }


def _trail_to_dict(trail, with_stops=False):
    data = {
        "id": trail.id,
        "slug": trail.slug,
        "title": trail.title,
        "summary": trail.summary,
        "description": trail.description,
        "image": trail_image(trail),
        "stop_count": trail.stop_count,
        "total_minutes": trail.total_minutes,
        "creator": {
            "username": trail.creator.username,
            "display": trail.creator.display,
        } if trail.creator else None,
        "created_at": trail.created_at.isoformat() if trail.created_at else None,
        "updated_at": trail.updated_at.isoformat() if trail.updated_at else None,
    }
    if with_stops:
        data["stops"] = [_trail_stop_to_dict(stop) for stop in trail.stops]
    return data


# ── Places ──────────────────────────────────────────────────────────

@api_bp.route("/places")
def list_places():
    """List approved places with optional search, filters and pagination."""
    q = (request.args.get("q") or "").strip()
    category = (request.args.get("category") or "").strip()
    governorate = (request.args.get("governorate") or "").strip()
    period = (request.args.get("period") or "").strip()
    sort = (request.args.get("sort") or "featured").strip()
    featured = request.args.get("featured")
    verified = request.args.get("verified")

    page, per_page = _paginate_args()

    query = query_places(q=q, category=category or None, governorate=governorate or None,
                         period=period or None, sort=sort)

    if featured and featured.lower() in ("1", "true", "yes"):
        query = query.where(HeritagePlace.featured == True)
    if verified and verified.lower() in ("1", "true", "yes"):
        query = query.where(HeritagePlace.verified == True)

    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return jsonify({
        "places": [_place_to_dict(p) for p in pagination.items],
        "pagination": _pagination_meta(pagination),
    })


@api_bp.route("/places/<slug>")
def get_place(slug):
    """Get a single place by slug (or numeric id)."""
    place = HeritagePlace.query.filter(
        HeritagePlace.status == "approved",
        db.or_(HeritagePlace.slug == slug, HeritagePlace.id == slug),
    ).first()
    if not place:
        return jsonify({"error": "Place not found"}), 404
    data = _place_to_dict(place)
    data["gallery"] = [
        {"path": item["path"], "url": item["url"], "caption": item["caption"]}
        for item in gallery_items(place)
    ]
    return jsonify(data)


# ── Stories ─────────────────────────────────────────────────────────

@api_bp.route("/stories")
def list_stories():
    """List stories with optional category/governorate filter and pagination."""
    category = (request.args.get("category") or "").strip()
    governorate = (request.args.get("governorate") or "").strip()
    q = (request.args.get("q") or "").strip()

    page, per_page = _paginate_args()

    query = select(Story).order_by(Story.created_at.desc())
    if category:
        query = query.where(Story.category == category)
    if governorate:
        query = query.where(Story.governorate == governorate)
    if q:
        terms = [t for t in q.split() if t.strip()]
        if terms:
            from sqlalchemy import or_
            like = lambda col: [col.ilike(f"%{t}%") for t in terms]
            query = query.where(or_(*like(Story.title), *like(Story.excerpt),
                                    *like(Story.author), *like(Story.category)))

    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return jsonify({
        "stories": [_story_to_dict(s) for s in pagination.items],
        "pagination": _pagination_meta(pagination),
    })


@api_bp.route("/stories/<slug>")
def get_story(slug):
    """Get a single story by slug (or numeric id)."""
    story = Story.query.filter(
        db.or_(Story.slug == slug, Story.id == slug),
    ).first()
    if not story:
        return jsonify({"error": "Story not found"}), 404
    return jsonify(_story_to_dict(story))


# ── Trails ──────────────────────────────────────────────────────────

@api_bp.route("/trails")
def list_trails():
    """List trails with optional search and pagination."""
    q = (request.args.get("q") or "").strip()
    page, per_page = _paginate_args()

    query = select(Trail).order_by(Trail.created_at.desc())
    if q:
        terms = [t for t in q.split() if t.strip()]
        if terms:
            from sqlalchemy import or_

            like = lambda col: [col.ilike(f"%{t}%") for t in terms]
            query = query.where(
                or_(*like(Trail.title), *like(Trail.summary), *like(Trail.description))
            )

    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
    return jsonify({
        "trails": [_trail_to_dict(t) for t in pagination.items],
        "pagination": _pagination_meta(pagination),
    })


@api_bp.route("/trails/<slug>")
def get_trail(slug):
    """Get a single trail (by slug or numeric id) with its stops."""
    trail = Trail.query.filter(db.or_(Trail.slug == slug, Trail.id == slug)).first()
    if not trail:
        return jsonify({"error": "Trail not found"}), 404
    return jsonify(_trail_to_dict(trail, with_stops=True))


# ── Categories ──────────────────────────────────────────────────────


@api_bp.route("/categories")
def list_categories():
    """List all categories with place counts."""
    cats = Category.query.order_by(Category.sort_order).all()
    counts = dict(
        db.session.execute(
            select(HeritagePlace.category_id, func.count(HeritagePlace.id))
            .where(HeritagePlace.status == "approved")
            .group_by(HeritagePlace.category_id)
        ).all()
    )
    return jsonify({
        "categories": [_category_to_dict(c, counts.get(c.id, 0)) for c in cats],
    })


# ── Radius Search ───────────────────────────────────────────────────

@api_bp.route("/nearby")
def nearby_places():
    """Find places within a radius of given coordinates.

    Required params: ``lat``, ``lng``
    Optional params: ``radius`` (km, default 50, max 500), ``q``, ``category``,
                     ``governorate``, ``period``, ``sort`` (default "distance"),
                     ``page``, ``per_page`` (default 20, max 100)
    """
    try:
        lat = float(request.args.get("lat", ""))
    except (TypeError, ValueError):
        return jsonify({"error": "lat is required and must be a number"}), 400
    try:
        lng = float(request.args.get("lng", ""))
    except (TypeError, ValueError):
        return jsonify({"error": "lng is required and must be a number"}), 400

    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return jsonify({"error": "lat must be -90..90, lng must be -180..180"}), 400

    try:
        radius_km = min(max(float(request.args.get("radius", 50)), 1), 500)
    except (TypeError, ValueError):
        radius_km = 50

    q = (request.args.get("q") or "").strip()
    category = (request.args.get("category") or "").strip()
    governorate = (request.args.get("governorate") or "").strip()
    period = (request.args.get("period") or "").strip()
    sort = (request.args.get("sort") or "distance").strip()

    page, per_page = _paginate_args()

    result = radius_search(
        lat=lat, lng=lng, radius_km=radius_km,
        q=q, category=category or None, governorate=governorate or None,
        period=period or None, sort=sort, page=page, per_page=per_page,
    )

    places_data = []
    for p in result["items"]:
        d = _place_to_dict(p)
        d["distance_km"] = p.distance_km
        places_data.append(d)

    return jsonify({
        "places": places_data,
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "pagination": {
            "page": result["page"],
            "per_page": result["per_page"],
            "total": result["total"],
            "pages": result["pages"],
            "has_next": result["page"] < result["pages"],
            "has_prev": result["page"] > 1,
        },
    })


# ── Stats ───────────────────────────────────────────────────────────

@api_bp.route("/stats")
def platform_stats():
    """Platform-wide statistics."""
    total_places = HeritagePlace.query.filter_by(status="approved").count()
    total_stories = Story.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()
    governorates = db.session.execute(
        select(func.count(func.distinct(HeritagePlace.governorate)))
        .where(HeritagePlace.status == "approved")
    ).scalar() or 0
    return jsonify({
        "total_places": total_places,
        "total_stories": total_stories,
        "total_users": total_users,
        "total_categories": total_categories,
        "governorates_covered": governorates,
    })
