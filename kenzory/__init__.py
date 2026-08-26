"""Kenzory application package.

Exposes the application-factory pattern via ``create_app()``. Configuration,
extensions, models, routes and services live in separate modules so the app
stays easy to extend in later milestones.
"""

import os

import click
from flask import Flask, render_template

from kenzory.config import get_config
from kenzory.constants import GOVERNORATES, PERIODS
from kenzory.extensions import db, login_manager, mail, migrate
from kenzory.services.places import place_image, story_image
from kenzory.services.security import get_csrf_token, protect_csrf

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")


def create_app(config_name=None, db_uri=None):
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
    app.config.from_object(get_config(config_name))
    if db_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    _register_blueprints(app)
    _register_template_helpers(app)
    _register_commands(app)

    @app.before_request
    def csrf_protect():
        return protect_csrf()

    return app


def _register_blueprints(app):
    from kenzory.routes.admin import admin_bp
    from kenzory.routes.auth import auth_bp
    from kenzory.routes.contributions import contributions_bp
    from kenzory.routes.errors import errors_bp
    from kenzory.routes.explore import explore_bp
    from kenzory.routes.main import main_bp
    from kenzory.routes.notifications import notifications_bp
    from kenzory.routes.places import places_bp
    from kenzory.routes.profile import profile_bp
    from kenzory.routes.reviews import reviews_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(explore_bp)
    app.register_blueprint(places_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(contributions_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(errors_bp)


def _register_template_helpers(app):
    from kenzory.models import Category

    @app.context_processor
    def inject_globals():
        categories = Category.query.order_by(Category.sort_order).all()
        category_meta = {
            c.name: {"icon": c.icon, "tone": c.tone, "slug": c.slug, "id": c.id}
            for c in categories
        }
        return {
            "categories": categories,
            "category_meta": category_meta,
            "governorates": GOVERNORATES,
            "periods": PERIODS,
            "csrf_token": get_csrf_token,
            "place_image": place_image,
            "story_image": story_image,
            "current_year": "2026",
        }

    @app.template_filter("stars")
    def stars(value):
        try:
            full = int(round(float(value or 0)))
        except (TypeError, ValueError):
            full = 0
        return ("★" * full) + ("☆" * max(0, 5 - full))

    @app.template_filter("num")
    def num(value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return "0"
        if value >= 1000:
            return f"{value / 1000:.1f}k".rstrip("0").rstrip(".")
        return str(value)

    @app.template_filter("timeago")
    def timeago(dt):
        from datetime import datetime

        if dt is None:
            return "recently"
        delta = datetime.utcnow() - dt
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            m = max(seconds // 60, 1)
            return f"{m} minute{'s' if m != 1 else ''} ago"
        if seconds < 86400:
            h = max(seconds // 3600, 1)
            return f"{h} hour{'s' if h != 1 else ''} ago"
        days = seconds // 86400
        if days < 30:
            return f"{days} day{'s' if days != 1 else ''} ago"
        if days < 365:
            months = days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"

    @app.template_filter("status_label")
    def status_label(value):
        return {
            "pending": "Pending review",
            "approved": "Approved",
            "rejected": "Rejected",
        }.get(value, value or "")

    @app.template_filter("status_tone")
    def status_tone(value):
        return {
            "pending": "st-pending",
            "approved": "st-approved",
            "rejected": "st-rejected",
        }.get(value, "")


def _register_commands(app):
    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Drop all tables and reseed from scratch.")
    def seed_command(reset):
        """Load development content (categories, places, stories, users)."""
        from kenzory.services.seed import run_seed

        with app.app_context():
            loaded = run_seed(reset=reset)
            if loaded:
                click.echo("Database seeded with development content.")
                click.echo("  Admin login: admin / Admin123! (change me in production)")
                click.echo("  Dev users:   <username>@kenzory.example / Kenzory123!")
            else:
                click.echo("Database already has content. Use --reset to reseed.")
