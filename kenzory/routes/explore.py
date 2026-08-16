"""Explore — database-backed search, filters, sorting and pagination."""

from flask import Blueprint, render_template, request

from kenzory.constants import EXPLORE_SORTS, GOVERNORATES, PERIODS
from kenzory.services.places import places_json
from kenzory.services.search import category_counts, paginate_places


def _arg(key, default=""):
    value = (request.args.get(key) or "").strip()
    return value if value else default


explore_bp = Blueprint("explore", __name__)


@explore_bp.route("/explore")
def explore():
    q = _arg("q")
    category = _arg("category")
    governorate = _arg("governorate")
    period = _arg("period")
    sort = _arg("sort", "featured")
    view = request.args.get("view", "grid")
    view = "list" if view == "list" else "grid"

    if sort not in EXPLORE_SORTS:
        sort = "featured"
    if governorate and governorate not in GOVERNORATES:
        governorate = ""
    if period and period not in PERIODS:
        period = ""

    try:
        page = max(int(request.args.get("page", 1)), 1)
    except (TypeError, ValueError):
        page = 1

    pagination = paginate_places(
        q=q,
        category=category,
        governorate=governorate,
        period=period,
        sort=sort,
        page=page,
    )

    return render_template(
        "explore.html",
        places=pagination.items,
        pagination=pagination,
        filters={
            "q": q,
            "category": category,
            "governorate": governorate,
            "period": period,
            "sort": sort,
            "view": view,
        },
        category_counts=category_counts(),
        governorates=GOVERNORATES,
        periods=PERIODS,
        sorts=EXPLORE_SORTS,
        places_json=places_json(pagination.items),
    )
