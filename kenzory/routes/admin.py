"""Admin dashboard and moderation."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from kenzory.auth import admin_required
from kenzory.extensions import db
from kenzory.models import Category, HeritagePlace, Submission, Trail, User
from kenzory.services.moderation import approve_submission, reject_submission

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
@admin_required
def _guard():
    """Every admin route requires an authenticated admin user."""


def _pagination(query):
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except (TypeError, ValueError):
        page = 1
    return db.paginate(
        query, page=page, per_page=current_app.config["ADMIN_PER_PAGE"], error_out=False
    )


@admin_bp.route("/")
def dashboard():
    status_count = dict(
        db.session.query(Submission.status, db.func.count(Submission.id))
        .group_by(Submission.status)
        .all()
    )
    place_status_count = dict(
        db.session.query(HeritagePlace.status, db.func.count(HeritagePlace.id))
        .group_by(HeritagePlace.status)
        .all()
    )
    stats = {
        "places": sum(place_status_count.values()),
        "approved_places": place_status_count.get("approved", 0),
        "pending": status_count.get("pending", 0),
        "approved_submissions": status_count.get("approved", 0),
        "rejected": status_count.get("rejected", 0),
        "users": db.session.query(db.func.count(User.id)).scalar() or 0,
        "categories": db.session.query(db.func.count(Category.id)).scalar() or 0,
        "trails": db.session.query(db.func.count(Trail.id)).scalar() or 0,
    }
    recent_submissions = (
        Submission.query.order_by(Submission.created_at.desc()).limit(8).all()
    )
    recent_places = (
        HeritagePlace.query.order_by(HeritagePlace.created_at.desc()).limit(8).all()
    )
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_submissions=recent_submissions,
        recent_places=recent_places,
    )


@admin_bp.route("/submissions")
def submissions():
    status = request.args.get("status", "pending")
    if status not in ("pending", "approved", "rejected", "all"):
        status = "pending"
    query = db.select(Submission).order_by(Submission.created_at.desc())
    if status != "all":
        query = query.where(Submission.status == status)
    pagination = _pagination(query)
    return render_template(
        "admin/submissions.html",
        submissions=pagination.items,
        pagination=pagination,
        status=status,
        counts=_submission_counts(),
    )


def _submission_counts():
    rows = db.session.query(Submission.status, db.func.count(Submission.id)).group_by(
        Submission.status
    )
    counts = {"pending": 0, "approved": 0, "rejected": 0, "all": 0}
    for status, count in rows:
        counts[status] = count
        counts["all"] += count
    return counts


@admin_bp.route("/submissions/<int:submission_id>")
def submission_detail(submission_id):
    submission = db.session.get(Submission, submission_id)
    if submission is None:
        flash("Submission not found.", "error")
        return redirect(url_for("admin.submissions"))
    return render_template("admin/submission_detail.html", submission=submission)


@admin_bp.route("/submissions/<int:submission_id>/approve", methods=["POST"])
def approve(submission_id):
    submission = db.session.get(Submission, submission_id)
    if submission is None:
        flash("Submission not found.", "error")
        return redirect(url_for("admin.submissions"))
    if submission.status == "approved":
        flash("This submission was already approved.", "info")
        return redirect(url_for("admin.submission_detail", submission_id=submission.id))

    from flask_login import current_user

    note = request.form.get("review_note", "")
    place = approve_submission(submission, reviewer=current_user, note=note)
    flash(f"Approved — “{place.title}” is now live.", "success")
    return redirect(url_for("admin.submissions", status="pending"))


@admin_bp.route("/submissions/<int:submission_id>/reject", methods=["POST"])
def reject(submission_id):
    submission = db.session.get(Submission, submission_id)
    if submission is None:
        flash("Submission not found.", "error")
        return redirect(url_for("admin.submissions"))
    if submission.status != "pending":
        flash("Only pending submissions can be rejected.", "info")
        return redirect(url_for("admin.submission_detail", submission_id=submission.id))

    from flask_login import current_user

    note = request.form.get("review_note", "")
    reject_submission(submission, reviewer=current_user, note=note)
    flash("Submission rejected. The contributor will see your note.", "info")
    return redirect(url_for("admin.submissions", status="pending"))


@admin_bp.route("/places")
def places():
    query = db.select(HeritagePlace).order_by(HeritagePlace.created_at.desc())
    pagination = _pagination(query)
    return render_template("admin/places.html", places=pagination.items, pagination=pagination)


@admin_bp.route("/users")
def users():
    query = db.select(User).order_by(User.created_at.desc())
    pagination = _pagination(query)
    return render_template("admin/users.html", users=pagination.items, pagination=pagination)


@admin_bp.route("/trails")
def trails():
    query = db.select(Trail).order_by(Trail.created_at.desc())
    pagination = _pagination(query)
    return render_template(
        "admin/trails.html", trails=pagination.items, pagination=pagination
    )


@admin_bp.route("/trails/<int:trail_id>/delete", methods=["POST"])
def delete_trail(trail_id):
    trail = db.session.get(Trail, trail_id)
    if trail is None:
        flash("Trail not found.", "error")
        return redirect(url_for("admin.trails"))
    db.session.delete(trail)
    db.session.commit()
    flash(f"Trail “{trail.title}” deleted.", "info")
    return redirect(url_for("admin.trails"))
