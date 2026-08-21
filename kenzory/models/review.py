"""Review model — community ratings and short reviews for heritage places.

One review per user per place (unique constraint); resubmitting updates the
existing row. ``HeritagePlace.rating`` / ``rating_count`` are denormalised
aggregates kept in sync by ``kenzory.services.reviews.recompute_rating``.
"""

from datetime import datetime

from kenzory.extensions import db

MIN_RATING = 1
MAX_RATING = 5
MAX_BODY_LENGTH = 1000


class Review(db.Model):
    __tablename__ = "reviews"
    __table_args__ = (
        db.UniqueConstraint("place_id", "user_id", name="uq_reviews_place_user"),
    )

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(
        db.Integer,
        db.ForeignKey("heritage_places.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating = db.Column(db.Integer, nullable=False)
    body = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    place = db.relationship("HeritagePlace", backref="reviews")
    user = db.relationship("User", backref="reviews")

    def __repr__(self):
        return f"<Review place={self.place_id} user={self.user_id} rating={self.rating}>"
