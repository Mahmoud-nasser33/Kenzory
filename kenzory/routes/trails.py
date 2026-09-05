"""Trail routes — curate published places into guided walking routes.

- ``/trails``             browse and search trails
- ``/trails/<slug>``      trail detail with ordered stops + map
- ``/trails/new``         create a trail from approved places
- ``/trails/<slug>/edit``   the creator (or an admin) edits a trail
- ``/trails/<slug>/delete`` the creator (or an admin) deletes a trail
"""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from kenzory.auth import login_required
from kenzory.extensions import db
from kenzory.models import HeritagePlace, Trail
from kenzory.services.trails import (
    MIN_SUMMARY_LENGTH,
    build_stops,
    ensure_trail_cover,
    picker_json,
    resolve_stops,
    unique_trail_slug,
)
from kenzory.models.trail import MAX_STOPS, MIN_STOPS

trails_bp = Blueprint("trails", __name__)


def _can_manage(trail):
    return current_user.is_admin or trail.created_by == current_user.id


def _approved_places():
    return (
        HeritagePlace.query.filter(HeritagePlace.status == "approved")
        .order_by(HeritagePlace.title.asc())
        .all()
    )


def _parse_trail_form():
    return {
        "title": request.form.get("title", "").strip(),
        "summary": request.form.get("summary", "").strip(),
        "description": request.form.get("description", "").strip(),
        "place_ids": request.form.get("place_ids", "").strip(),
    }


def _validate(form, places_count):
    errors = {}
    if len(form["title"]) < 3:
        errors["title"] = "Please give the trail a name (at least 3 characters)."
    if len(form["summary"]) < MIN_SUMMARY_LENGTH:
        errors["summary"] = (
            "Please describe the route — at least two sentences about what it covers."
        )
    if places_count < MIN_STOPS:
        errors["places"] = f"A trail needs at least {MIN_STOPS} places."
    if places_count > MAX_STOPS:
        errors["places"] = f"A trail can include at most {MAX_STOPS} places."
    return errors


# ---------------------------------------------------------------------------
# Browse + detail
# ---------------------------------------------------------------------------


@trails_bp.route("/trails")
def trail_list():
    query = Trail.query
    q = (request.args.get("q") or "").strip()
    if q:
        query = query.filter(
            Trail.title.ilike(f"%{q}%")
            | Trail.summary.ilike(f"%{q}%")
            | Trail.description.ilike(f"%{q}%")
        )
    trails = query.order_by(Trail.created_at.desc()).all()
    return render_template("trails.html", trails=trails, q=q)


@trails_bp.route("/trails/<slug>")
def trail_detail(slug):
    trail = Trail.query.filter(Trail.slug == slug).first_or_404()
    stop_meta = [
        {
            "id": stop.place.slug,
            "name": stop.place.title,
            "latitude": stop.place.latitude,
            "longitude": stop.place.longitude,
            "category": stop.place.category.name if stop.place.category else "",
        }
        for stop in trail.stops
    ]
    return render_template("trail.html", trail=trail, stop_meta=stop_meta)


# ---------------------------------------------------------------------------
# Create / edit / delete
# ---------------------------------------------------------------------------


@trails_bp.route("/trails/new", methods=["GET", "POST"])
@login_required
def new_trail():
    places = _approved_places()
    form = {}
    errors = {}

    if request.method == "POST":
        form = _parse_trail_form()
        ordered = resolve_stops(_split_ids(form["place_ids"]))
        errors = _validate(form, len(ordered))
        if not errors:
            trail = Trail(
                slug=unique_trail_slug(form["title"]),
                title=form["title"],
                summary=form["summary"],
                description=form["description"] or form["summary"],
                created_by=current_user.id,
            )
            db.session.add(trail)
            db.session.flush()
            build_stops(trail, ordered)
            ensure_trail_cover(trail)
            db.session.commit()
            flash(f"“{trail.title}” is live — thanks for curating it!", "success")
            return redirect(url_for("trails.trail_detail", slug=trail.slug))

        form["place_ids"] = list(dict.fromkeys([str(p.id) for p in ordered]))

    return render_template(
        "trail_form.html",
        form=form,
        errors=errors,
        places=places,
        places_picker=picker_json(places),
        mode="new",
    )


@trails_bp.route("/trails/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_trail(slug):
    trail = Trail.query.filter(Trail.slug == slug).first_or_404()
    if not _can_manage(trail):
        abort(403)

    places = _approved_places()
    errors = {}

    if request.method == "POST":
        form = _parse_trail_form()
        ordered = resolve_stops(_split_ids(form["place_ids"]))
        errors = _validate(form, len(ordered))
        if not errors:
            trail.title = form["title"]
            trail.summary = form["summary"]
            trail.description = form["description"] or form["summary"]
            build_stops(trail, ordered)
            ensure_trail_cover(trail)
            db.session.commit()
            flash("Your trail has been updated.", "success")
            return redirect(url_for("trails.trail_detail", slug=trail.slug))
    else:
        form = {
            "title": trail.title,
            "summary": trail.summary,
            "description": trail.description,
            "place_ids": [str(stop.place_id) for stop in trail.stops],
        }

    return render_template(
        "trail_form.html",
        form=form,
        errors=errors,
        places=places,
        places_picker=picker_json(places),
        mode="edit",
        trail=trail,
    )


@trails_bp.route("/trails/<slug>/delete", methods=["POST"])
@login_required
def delete_trail(slug):
    trail = Trail.query.filter(Trail.slug == slug).first_or_404()
    if not _can_manage(trail):
        abort(403)
    db.session.delete(trail)
    db.session.commit()
    flash("Trail deleted.", "info")
    return redirect(url_for("trails.trail_list"))


def _split_ids(raw):
    """Parse a comma/whitespace separated list of place ids."""
    parts = [p.strip() for p in raw.replace(",", " ").split() if p.strip()]
    seen = []
    for pid in parts:
        if pid not in seen:
            seen.append(pid)
    return seen