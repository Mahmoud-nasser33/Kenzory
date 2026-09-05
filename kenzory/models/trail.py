"""Trail model — user-curated walking routes linking heritage places.

A trail is an ordered sequence of already-approved places. Because every stop
is a published HeritagePlace, trails are shown publicly as soon as they are
created; admins can remove any trail that breaks the platform guidelines.
"""

from datetime import datetime

from kenzory.extensions import db

MIN_STOPS = 2
MAX_STOPS = 30


class Trail(db.Model):
    __tablename__ = "trails"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    image = db.Column(db.String(255))

    created_by = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    creator = db.relationship(
        "User", backref="trails", lazy=True, foreign_keys=[created_by]
    )

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    stops = db.relationship(
        "TrailStop",
        backref="trail",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="TrailStop.position",
    )

    def __repr__(self):
        return f"<Trail {self.slug!r}>"

    @property
    def stop_count(self):
        return len(self.stops)

    @property
    def places(self):
        return [stop.place for stop in self.stops]

    @property
    def total_minutes(self):
        return sum((stop.place.visit_minutes or 60) for stop in self.stops)

    @property
    def first_place(self):
        return self.stops[0].place if self.stops else None


class TrailStop(db.Model):
    __tablename__ = "trail_stops"

    id = db.Column(db.Integer, primary_key=True)
    trail_id = db.Column(
        db.Integer, db.ForeignKey("trails.id", ondelete="CASCADE"), nullable=False, index=True
    )
    place_id = db.Column(
        db.Integer,
        db.ForeignKey("heritage_places.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position = db.Column(db.Integer, nullable=False, default=0)
    note = db.Column(db.String(500))

    place = db.relationship("HeritagePlace", lazy="joined")

    __table_args__ = (db.UniqueConstraint("trail_id", "place_id", name="uq_trail_stop"),)

    def __repr__(self):
        return f"<TrailStop trail={self.trail_id} place={self.place_id} pos={self.position}>"