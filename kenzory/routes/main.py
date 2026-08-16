"""Public marketing + discovery pages: home, about, discoveries, map, stories."""

from flask import Blueprint, render_template

from kenzory.extensions import db
from kenzory.models import Category, HeritagePlace, Story, User
from kenzory.services.places import places_json

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    approved = HeritagePlace.status == "approved"

    featured = (
        HeritagePlace.query.filter(approved, HeritagePlace.featured.is_(True))
        .order_by(HeritagePlace.rating.desc())
        .limit(6)
        .all()
    )
    popular = (
        HeritagePlace.query.filter(approved)
        .order_by(HeritagePlace.saves.desc())
        .limit(3)
        .all()
    )
    recent = (
        HeritagePlace.query.filter(approved)
        .order_by(HeritagePlace.created_at.desc())
        .limit(6)
        .all()
    )
    categories = Category.query.order_by(Category.sort_order).all()
    places_by_category = dict(
        db.session.query(Category.id, db.func.count(HeritagePlace.id))
        .join(HeritagePlace, HeritagePlace.category_id == Category.id)
        .filter(approved)
        .group_by(Category.id)
        .all()
    )

    lead_story = Story.query.order_by(Story.created_at.desc()).first()
    side_stories = (
        Story.query.filter(Story.id != (lead_story.id if lead_story else -1))
        .order_by(Story.created_at.desc())
        .limit(2)
        .all()
    )

    top_contributors = (
        User.query.join(HeritagePlace, HeritagePlace.created_by == User.id)
        .filter(approved)
        .group_by(User.id)
        .order_by(db.func.count(HeritagePlace.id).desc())
        .limit(5)
        .all()
    )

    total_places = db.session.query(db.func.count(HeritagePlace.id)).filter(approved).scalar() or 0
    total_photos = (
        db.session.query(db.func.coalesce(db.func.sum(HeritagePlace.photos), 0))
        .filter(approved)
        .scalar()
        or 0
    )
    governorates_count = (
        db.session.query(HeritagePlace.governorate).filter(approved).distinct().count()
    )

    return render_template(
        "index.html",
        featured=featured,
        popular=popular,
        recent=recent,
        categories=categories,
        places_by_category=places_by_category,
        lead_story=lead_story,
        side_stories=side_stories,
        top_contributors=top_contributors,
        stats={
            "places": total_places,
            "photos": int(total_photos),
            "governorates": governorates_count,
        },
        places_json=places_json(featured + recent),
    )


@main_bp.route("/about")
def about():
    approved = HeritagePlace.status == "approved"
    total_places = db.session.query(db.func.count(HeritagePlace.id)).filter(approved).scalar() or 0
    total_photos = (
        db.session.query(db.func.coalesce(db.func.sum(HeritagePlace.photos), 0))
        .filter(approved)
        .scalar()
        or 0
    )
    governorates_count = (
        db.session.query(HeritagePlace.governorate).filter(approved).distinct().count()
    )
    top_contributors = (
        User.query.join(HeritagePlace, HeritagePlace.created_by == User.id)
        .filter(approved)
        .group_by(User.id)
        .order_by(db.func.count(HeritagePlace.id).desc())
        .limit(6)
        .all()
    )
    contributor_counts = dict(
        db.session.query(
            HeritagePlace.created_by, db.func.count(HeritagePlace.id)
        )
        .filter(approved)
        .group_by(HeritagePlace.created_by)
        .all()
    )
    active_contributors = len(contributor_counts)
    return render_template(
        "about.html",
        stats={
            "places": total_places,
            "photos": int(total_photos),
            "governorates": governorates_count,
            "contributors": active_contributors,
        },
        top_contributors=top_contributors,
        contributor_counts=contributor_counts,
    )


@main_bp.route("/discoveries")
def discoveries():
    recent_places = (
        HeritagePlace.query.filter(HeritagePlace.status == "approved")
        .order_by(HeritagePlace.created_at.desc())
        .limit(10)
        .all()
    )
    recent_stories = Story.query.order_by(Story.created_at.desc()).limit(4).all()
    return render_template(
        "discoveries.html",
        recent_places=recent_places,
        recent_stories=recent_stories,
    )


@main_bp.route("/saved")
def saved():
    places = HeritagePlace.query.filter(HeritagePlace.status == "approved").all()
    return render_template("saved.html", places_json=places_json(places))


@main_bp.route("/map")
def map_page():
    places = HeritagePlace.query.filter(HeritagePlace.status == "approved").all()
    return render_template("map.html", places_json=places_json(places))


@main_bp.route("/stories")
def stories():
    query = Story.query.order_by(Story.created_at.desc())
    q = _request_arg("q")
    if q:
        query = query.filter(Story.title.ilike(f"%{q}%") | Story.excerpt.ilike(f"%{q}%"))
    return render_template("stories.html", stories=query.all(), q=q)


@main_bp.route("/stories/<slug>")
def story_detail(slug):
    story = Story.query.filter(Story.slug == slug).first_or_404()
    related = (
        Story.query.filter(Story.id != story.id).order_by(Story.created_at.desc()).limit(3).all()
    )
    return render_template(
        "story.html",
        story=story,
        related_stories=related,
    )


def _request_arg(key):
    from flask import request

    return (request.args.get(key) or "").strip()
