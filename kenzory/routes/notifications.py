"""Notification routes — in-app notification center."""

from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from kenzory.auth import login_required
from kenzory.services.notifications import (
    all_notifications,
    mark_all_read,
    mark_read,
    recent_notifications,
    unread_count,
)

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    pagination = all_notifications(current_user.id, page=page)
    return render_template("notifications.html", pagination=pagination)


@notifications_bp.route("/<int:notif_id>/read", methods=["POST"])
@login_required
def read_one(notif_id):
    mark_read(notif_id, current_user.id)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True})
    return redirect(url_for("notifications.index"))


@notifications_bp.route("/read-all", methods=["POST"])
@login_required
def mark_all():
    mark_all_read(current_user.id)
    return redirect(url_for("notifications.index"))


@notifications_bp.route("/unread-count")
@login_required
def api_unread_count():
    return jsonify({"count": unread_count(current_user.id)})


@notifications_bp.route("/recent")
@login_required
def api_recent():
    notifs = recent_notifications(current_user.id, limit=8)
    return jsonify(
        {
            "notifications": [
                {
                    "id": n.id,
                    "type": n.type,
                    "title": n.title,
                    "message": n.message,
                    "link": n.link or "#",
                    "is_read": n.is_read,
                    "time": n.created_at.strftime("%b %d, %Y"),
                }
                for n in notifs
            ]
        }
    )
