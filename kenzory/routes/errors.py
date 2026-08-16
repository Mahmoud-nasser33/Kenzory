"""Friendly error pages."""

from flask import Blueprint, render_template

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(400)
def bad_request(error):
    return render_template("errors/400.html", message=getattr(error, "description", None)), 400


@errors_bp.app_errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403


@errors_bp.app_errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@errors_bp.app_errorhandler(413)
def too_large(error):
    return render_template("errors/413.html"), 413


@errors_bp.app_errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500
