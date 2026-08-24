"""Contribution routes — the community's way to document heritage places.

Covers the full contribution lifecycle:

- ``/add-place``          submit a new place for moderation (with captioned photos)
- ``/place/<slug>/edit``  contributors and admins refine an existing record
- ``/community-review``   browse pending submissions and endorse them
- ``/submissions/<id>/vote``  toggle the current user's endorsement
"""

import os

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user

from kenzory.auth import login_required
from kenzory.constants import GOVERNORATES, PERIODS
from kenzory.extensions import db
from kenzory.models import Category, HeritagePlace, Submission
from kenzory.services.gallery import (
    append_uploads,
    apply_gallery_edits,
    clean_caption,
    pair_captions,
)
from kenzory.services.images import save_upload
from kenzory.services.votes import toggle_vote, user_voted_ids, vote_counts_map

contributions_bp = Blueprint("contributions", __name__)

MAX_PHOTOS = 5


def _valid_category(category_id):
    if not category_id:
        return None
    try:
        return db.session.get(Category, int(category_id))
    except (TypeError, ValueError):
        return None


def _float_or_none(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_place_form():
    """Read the shared add/edit place fields from the request."""
    return {
        "title": request.form.get("title", "").strip(),
        "title_ar": request.form.get("title_ar", "").strip(),
        "summary": request.form.get("summary", "").strip(),
        "description": request.form.get("description", "").strip(),
        "historical_information": request.form.get("historical_information", "").strip(),
        "location": request.form.get("location", "").strip(),
        "governorate": request.form.get("governorate", "").strip(),
        "period": request.form.get("period", "").strip(),
        "sources": request.form.get("sources", "").strip(),
        "latitude": _float_or_none(request.form.get("latitude")),
        "longitude": _float_or_none(request.form.get("longitude")),
        "terms": request.form.get("terms") == "on",
    }


def _save_uploads(files):
    """Save uploaded photos, removing any already saved if one fails."""
    saved = []
    try:
        for file_storage in files[:MAX_PHOTOS] if files else []:
            if file_storage and file_storage.filename:
                saved.append(save_upload(file_storage))
    except ValueError:
        _delete_saved(saved)
        raise
    return saved


def _delete_saved(paths):
    folder = _upload_folder()
    for rel in paths:
        try:
            os.remove(os.path.join(folder, os.path.basename(rel)))
        except OSError:
            pass


def _upload_folder():
    from flask import current_app

    return current_app.config["UPLOAD_FOLDER"]


# ---------------------------------------------------------------------------
# Submit a new place
# ---------------------------------------------------------------------------


@contributions_bp.route("/add-place", methods=["GET", "POST"])
@login_required
def add_place():
    categories = Category.query.order_by(Category.sort_order).all()
    form = {}
    errors = {}
    submitted = None

    if request.method == "POST":
        form = _parse_place_form()
        category = _valid_category(request.form.get("category"))
        errors = _validate(form, category)

        saved_paths = []
        if not errors:
            try:
                saved_paths = _save_uploads(request.files.getlist("photos"))
            except ValueError as exc:
                errors["photos"] = str(exc)

        if not errors:
            submission = Submission(
                title=form["title"],
                title_ar=form["title_ar"],
                summary=form["summary"],
                description=form["description"],
                historical_information=form["historical_information"],
                sources=form["sources"],
                location=form["location"],
                governorate=form["governorate"],
                period=form["period"] or None,
                latitude=form["latitude"],
                longitude=form["longitude"],
                images=saved_paths,
                image_captions=pair_captions(
                    saved_paths, request.form.getlist("photo_captions")
                ),
                category_id=category.id,
                submitted_by=current_user.id,
                status="pending",
            )
            db.session.add(submission)
            db.session.commit()
            submitted = submission
            flash(
                "Your discovery has been submitted. Reviewers will take a look soon.",
                "success",
            )

    return render_template(
        "add_place.html",
        categories=categories,
        governorates=GOVERNORATES,
        periods=PERIODS,
        form=form,
        errors=errors,
        submitted=submitted,
    )


def _validate(form, category):
    errors = {}
    if len(form["title"]) < 3:
        errors["title"] = "Please enter the place name (at least 3 characters)."
    if category is None:
        errors["category"] = "Please choose a category."
    if form["governorate"] not in GOVERNORATES:
        errors["governorate"] = "Please choose a governorate."
    if not form["location"]:
        errors["location"] = "Please enter the nearest city or area."
    if len(form["summary"]) < 20:
        errors["summary"] = (
            "Please tell us a little more about the place — at least two sentences "
            "explaining what it is and why it matters."
        )
    if not form["terms"]:
        errors["terms"] = "Please confirm your record is accurate to the best of your knowledge."
    return errors


@contributions_bp.route("/submissions")
@login_required
def my_submissions():
    submissions = (
        Submission.query.filter_by(submitted_by=current_user.id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    counts = vote_counts_map([s for s in submissions if s.status == "pending"])
    return render_template("submissions.html", submissions=submissions, vote_counts=counts)


# ---------------------------------------------------------------------------
# Edit an existing place (creator or admin)
# ---------------------------------------------------------------------------


def _can_edit(place):
    return current_user.is_admin or place.created_by == current_user.id


@contributions_bp.route("/place/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit_place(slug):
    place = HeritagePlace.query.filter_by(slug=slug, status="approved").first_or_404()
    if not _can_edit(place):
        abort(403)

    categories = Category.query.order_by(Category.sort_order).all()
    gallery = list(place.gallery or [])
    captions = dict(place.photo_captions or {})

    if request.method == "POST":
        form = _parse_place_form()
        category = _valid_category(request.form.get("category"))
        errors = _validate(form, category)

        # Existing photos: which were kept, and their updated captions.
        kept_paths = []
        kept_captions = {}
        for index in range(len(gallery)):
            if request.form.get(f"keep_{index}") == "on":
                path = request.form.get(f"path_{index}", "")
                if path in gallery and path not in kept_paths:
                    kept_paths.append(path)
                    caption = clean_caption(request.form.get(f"caption_{index}"))
                    if caption:
                        kept_captions[path] = caption

        new_paths = []
        if not errors:
            try:
                new_paths = _save_uploads(request.files.getlist("new_photos"))
            except ValueError as exc:
                errors["photos"] = str(exc)

        total_kept = len(kept_paths) + len(new_paths)
        if not errors and total_kept == 0 and bool(gallery):
            errors["photos"] = "A record needs at least one photo — keep or upload one."

        if not errors:
            form_category_id = category.id
            place.title = form["title"]
            place.title_ar = form["title_ar"]
            place.summary = form["summary"]
            place.description = form["description"]
            place.historical_background = form["historical_information"] or None
            place.location = form["location"]
            place.governorate = form["governorate"]
            place.period = form["period"] or None
            place.sources = [form["sources"]] if form["sources"] else []
            place.latitude = form["latitude"]
            place.longitude = form["longitude"]
            place.category_id = form_category_id

            apply_gallery_edits(place, kept_paths, kept_captions)
            append_uploads(
                place,
                new_paths,
                pair_captions(new_paths, request.form.getlist("photo_captions")),
            )

            db.session.commit()
            flash("Your edits have been saved.", "success")
            return redirect(url_for("places.place_detail", slug=place.slug))

        # Re-render with submitted values.
        form["category"] = request.form.get("category")
    else:
        form = {
            "title": place.title,
            "title_ar": place.title_ar or "",
            "summary": place.summary,
            "description": place.description or "",
            "historical_information": place.historical_background or "",
            "location": place.location,
            "governorate": place.governorate,
            "period": place.period or "",
            "sources": (place.sources or [""])[0] if place.sources else "",
            "latitude": place.latitude,
            "longitude": place.longitude,
            "terms": False,
            "category": str(place.category_id),
        }
        errors = {}

    return render_template(
        "edit_place.html",
        place=place,
        categories=categories,
        governorates=GOVERNORATES,
        periods=PERIODS,
        form=form,
        errors=errors,
        gallery=gallery,
        captions=captions,
    )


# ---------------------------------------------------------------------------
# Community review queue + voting
# ---------------------------------------------------------------------------


@contributions_bp.route("/community-review")
@login_required
def community_review():
    pending = (
        Submission.query.filter_by(status="pending")
        .order_by(Submission.created_at.desc())
        .all()
    )
    # Most-endorsed first; the stable sort keeps newer records ahead on ties.
    pending.sort(key=lambda s: len(s.votes), reverse=True)

    counts = vote_counts_map(pending)
    voted = user_voted_ids(current_user.id, [s.id for s in pending])
    return render_template(
        "community_review.html",
        submissions=pending,
        vote_counts=counts,
        voted_ids=voted,
    )


@contributions_bp.route("/submissions/<int:submission_id>/vote", methods=["POST"])
@login_required
def vote(submission_id):
    submission = db.session.get(Submission, submission_id)
    if submission is None or submission.status != "pending":
        abort(404)
    if submission.submitted_by == current_user.id:
        flash("You can't vote for your own submission — invite others to!", "info")
        return redirect(url_for("contributions.community_review"))

    voted, count = toggle_vote(submission, current_user)
    if voted:
        flash(f"Endorsement added — this record now has {count} vote{'s' if count != 1 else ''}.", "success")
    else:
        flash("Your endorsement was removed.", "info")
    return redirect(url_for("contributions.community_review"))
