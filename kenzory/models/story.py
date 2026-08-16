"""Story model — long-form editorial content linked to a heritage place."""

from datetime import datetime

from kenzory.extensions import db


class Story(db.Model):
    __tablename__ = "stories"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    excerpt = db.Column(db.Text, nullable=False, default="")
    author = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120))
    read_minutes = db.Column(db.Integer, nullable=False, default=5)
    date = db.Column(db.String(40))
    image = db.Column(db.String(255))
    governorate = db.Column(db.String(120))
    category = db.Column(db.String(120))
    content = db.Column(db.JSON, default=list)

    place_id = db.Column(
        db.Integer, db.ForeignKey("heritage_places.id", ondelete="SET NULL"), index=True
    )
    place = db.relationship("HeritagePlace", backref="stories", lazy=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Story {self.slug!r}>"
