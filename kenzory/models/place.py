"""HeritagePlace model — the core content entity of Kenzory.

Only records with status == "approved" are shown publicly. Rich editorial
content (key facts, timeline, architecture, local stories, sources, gallery)
is stored as JSON columns so the detail page keeps the depth of a curated
record without a dozen join tables.
"""

from datetime import datetime

from kenzory.extensions import db

STATUS_APPROVED = "approved"
STATUS_PENDING = "pending"
STATUS_REJECTED = "rejected"
PUBLIC_STATUSES = (STATUS_APPROVED,)


class HeritagePlace(db.Model):
    __tablename__ = "heritage_places"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    summary = db.Column(db.Text, nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    historical_background = db.Column(db.Text)

    location = db.Column(db.String(255), nullable=False, default="")
    region = db.Column(db.String(255))
    governorate = db.Column(db.String(120), nullable=False, index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True
    )
    period = db.Column(db.String(120))
    approx_date = db.Column(db.String(120))

    image = db.Column(db.String(255))  # relative path inside /static
    gallery = db.Column(db.JSON, default=list)
    # Maps gallery path -> caption text (parallel to ``gallery``).
    photo_captions = db.Column(db.JSON, default=dict)

    key_facts = db.Column(db.JSON, default=list)
    timeline = db.Column(db.JSON, default=list)
    architecture = db.Column(db.JSON, default=list)
    local_stories = db.Column(db.JSON, default=list)
    sources = db.Column(db.JSON, default=list)

    rating = db.Column(db.Float, nullable=False, default=0.0)
    rating_count = db.Column(db.Integer, nullable=False, default=0)
    saves = db.Column(db.Integer, nullable=False, default=0)
    photos = db.Column(db.Integer, nullable=False, default=0)
    visit_minutes = db.Column(db.Integer, nullable=False, default=60)
    distance_km = db.Column(db.Float, nullable=False, default=0.0)

    verified = db.Column(db.Boolean, nullable=False, default=False)
    featured = db.Column(db.Boolean, nullable=False, default=False)
    popular = db.Column(db.Boolean, nullable=False, default=False)

    status = db.Column(db.String(20), nullable=False, default=STATUS_APPROVED, index=True)
    created_by = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<HeritagePlace {self.slug!r}>"
