"""Contribution routes — the community's way to document heritage places."""

import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user

from kenzory.auth import login_required
from kenzory.constants import GOVERNORATES, PERIODS
from kenzory.extensions import db
from kenzory.models import Category, Submission
from kenzory.services.images import save_upload

contributions_bp = Blueprint("contributions", __name__)


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


@contributions_bp.route("/add-place", methods=["GET", "POST"])
@login_required
def add_place():
    categories = Category.query.order_by(Category.sort_order).all()
    form = {}
    errors = {}
    submitted = None

    if request.method == "POST":
        form = {
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


def _save_uploads(files):
    """Save uploaded photos, removing any already saved if one fails."""
    saved = []
    try:
        for file_storage in files:
            if file_storage and file_storage.filename:
                saved.append(save_upload(file_storage))
    except ValueError:
        _delete_saved(saved)
        raise
    return saved


def _delete_saved(paths):
    folder = current_app.config["UPLOAD_FOLDER"]
    for rel in paths:
        try:
            os.remove(os.path.join(folder, os.path.basename(rel)))
        except OSError:
            pass


@contributions_bp.route("/submissions")
@login_required
def my_submissions():
    submissions = (
        Submission.query.filter_by(submitted_by=current_user.id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    return render_template("submissions.html", submissions=submissions)
