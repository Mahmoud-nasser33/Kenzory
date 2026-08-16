"""Explore search and filtering.

All filtering, sorting and pagination happens in the database. The browser
never receives the full table — it only ever gets one page of results.
"""

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
}


def _text_terms(text):
    return [t for t in text.split() if t.strip()]


def query_places(q="", category=None, governorate=None, period=None, sort="featured"):
    query = select(HeritagePlace).where(HeritagePlace.status == "approved")

    if q:
        terms = _text_terms(q)
        if terms:
            like = lambda column: [column.ilike(f"%{term}%") for term in terms]
            query = query.where(
                or_(
                    *like(HeritagePlace.title),
                    *like(HeritagePlace.title_ar),
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
    return query.order_by(*order)


def paginate_places(q="", category=None, governorate=None, period=None, sort="featured", page=1):
    query = query_places(
        q=q, category=category, governorate=governorate, period=period, sort=sort
    )
    return db.paginate(
        query, page=page, per_page=current_app.config["PER_PAGE"], error_out=False
    )


def category_counts():
    """Approved place counts keyed by category slug, for Explore chips."""
    rows = db.session.execute(
        select(Category.slug, db.func.count(HeritagePlace.id))
        .join(HeritagePlace, HeritagePlace.category_id == Category.id)
        .where(HeritagePlace.status == "approved")
        .group_by(Category.slug)
    ).all()
    return {slug: total for slug, total in rows}
