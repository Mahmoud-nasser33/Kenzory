"""Category model — database-backed taxonomy for heritage places."""

from kenzory.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    description = db.Column(db.String(500))
    icon = db.Column(db.String(80), nullable=False, default="map-pin")
    tone = db.Column(db.String(40), nullable=False, default="cat-hidden")
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    places = db.relationship("HeritagePlace", backref="category", lazy=True)
    submissions = db.relationship("Submission", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name!r}>"
