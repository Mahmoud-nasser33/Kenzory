"""User profiles — own profile and public contributor pages."""

from flask import Blueprint, abort, render_template
from flask_login import current_user

from kenzory.auth import login_required
from kenzory.models import HeritagePlace, User
from kenzory.services.profile import get_profile_data, LEVELS

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    data = get_profile_data(current_user)
    data["max_reputation"] = _next_level_threshold(data["reputation"])
    return render_template("profile.html", **data)


@profile_bp.route("/contributor/<username>")
def contributor(username):
    user = User.query.filter_by(username=username).first_or_404()
    data = get_profile_data(user)
    data["max_reputation"] = _next_level_threshold(data["reputation"])
    return render_template("contributor.html", **data)


def _next_level_threshold(reputation):
    """Return the next reputation threshold for the progress bar."""
    for threshold, _name in LEVELS:
        if reputation < threshold:
            return threshold
    return LEVELS[-1][0]
