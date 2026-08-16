"""Development seed loader.

Loads realistic Egyptian heritage content from ``kenzory.seed_data`` into the
database. This runs only on demand via ``flask seed`` and is intentionally
separate from application logic and production data.
"""

import os
from datetime import datetime, timedelta

from flask import current_app

from kenzory import seed_data
from kenzory.extensions import db
from kenzory.models import Category, HeritagePlace, Story, User
from kenzory.services.covers import ensure_cover

DEV_PASSWORD = os.getenv("KENZORY_SEED_PASSWORD", "Kenzory123!")
ADMIN_PASSWORD = os.getenv("KENZORY_ADMIN_PASSWORD", "Admin123!")

# Curated subset for the demo build: only these places/stories are seeded.
# Each selected place has a real photograph in static/img, and galleries are
# kept to a single image so no fabricated covers are shown.
CURATED_PLACES = {
    "deir-al-qusayr",
    "mosque-al-hamawi",
    "nubian-village",
    "satis-palace",
    "station-deir-sharaf",
    "temple-of-nefertari",
    "meidum",
}

CURATED_STORIES = {
    "mosque-village-forgot",
    "second-life-village",
    "incorrupt-bishop",
    "ghost-station-clock",
}


def _has_content():
    return db.session.query(Category.id).first() is not None


def _resolve_image(key, slug, category, name_ar, name_en, city):
    """Map a prototype image key to a static path (photo or generated cover)."""
    base = current_app.static_folder
    if key:
        jpg = os.path.join(base, "img", f"{key}.jpg")
        if os.path.isfile(jpg):
            return f"img/{key}.jpg"
    return ensure_cover(slug, category, name_ar, name_en, city)


def seed_users():
    users = []
    for username, meta in seed_data.CONTRIBUTORS.items():
        user = User(
            username=username,
            email=f"{username}@kenzory.example",
            display_name=meta["name"],
            role="user",
        )
        user.set_password(DEV_PASSWORD)
        db.session.add(user)
        users.append(user)

    admin = User(
        username="admin",
        email="admin@kenzory.example",
        display_name="Kenzory Admin",
        role="admin",
    )
    admin.set_password(ADMIN_PASSWORD)
    db.session.add(admin)
    users.append(admin)
    db.session.flush()
    return {u.username: u for u in users}


def seed_categories():
    categories = []
    for index, name in enumerate(seed_data.CATEGORIES):
        meta = seed_data.CATEGORY_META.get(name, {})
        cat = Category(
            name=name,
            slug=name.lower().replace(" & ", "-").replace(" ", "-"),
            description=_CATEGORY_DESCRIPTIONS.get(name, ""),
            icon=meta.get("icon", "map-pin"),
            tone=meta.get("tone", "cat-hidden"),
            sort_order=index,
        )
        db.session.add(cat)
        categories.append(cat)
    db.session.flush()
    return {c.name: c for c in categories}


_CATEGORY_DESCRIPTIONS = {
    "Historical Sites": "Monumental and archaeological sites of every era.",
    "Hidden Gems": "Little-known places that rarely make the guidebooks.",
    "Architecture": "Buildings, gates, palaces, stations and their craft.",
    "Traditional Crafts": "Living workshops and craft traditions.",
    "Food & Culture": "Coffeehouses, kitchens and cultural meeting points.",
    "Stories & Legends": "Places carried by the stories told about them.",
    "Religious Heritage": "Monasteries, mosques, churches and sacred sites.",
    "Natural Heritage": "Landscapes and natural wonders.",
}


def seed_places(categories, users):
    recent_rank = {pid: i for i, pid in enumerate(seed_data.RECENT_ORDER)}
    places = []
    for raw in seed_data.PLACES:
        if raw["id"] not in CURATED_PLACES:
            continue
        cat = categories[raw["category"]]
        user = users.get(raw.get("contributor", ""), users["mahmoud"])
        slug = raw["id"]
        name_en = raw["name"].split(" — ")[0]
        image = _resolve_image(
            raw.get("image"),
            slug,
            raw["category"],
            raw.get("nameAr", ""),
            name_en,
            raw.get("city", ""),
        )
        gallery = [image]

        created_offset = recent_rank.get(slug, 0)
        created_at = datetime.utcnow() - timedelta(days=3 + created_offset * 5)

        place = HeritagePlace(
            slug=slug,
            title=raw["name"],
            title_ar=raw.get("nameAr", ""),
            summary=raw["summary"],
            description=raw["description"],
            historical_background=raw["description"],
            location=raw.get("city", ""),
            region=raw.get("region", ""),
            governorate=raw["governorate"],
            latitude=raw["lat"],
            longitude=raw["lng"],
            category=cat,
            period=raw.get("period", ""),
            approx_date=raw.get("approxDate", ""),
            image=image,
            gallery=gallery,
            key_facts=raw.get("keyFacts", []),
            timeline=raw.get("timeline", []),
            architecture=raw.get("architecture", []),
            local_stories=raw.get("stories", []),
            sources=raw.get("sources", []),
            rating=raw.get("rating", 0),
            rating_count=raw.get("ratingCount", 0),
            saves=raw.get("saves", 0),
            photos=1,
            visit_minutes=raw.get("visitMinutes", 60),
            distance_km=raw.get("distanceKm", 0),
            verified=raw.get("verified", False),
            featured=raw.get("featured", False),
            popular=raw.get("popular", False),
            status="approved",
            created_by=user.id,
            created_at=created_at,
        )
        db.session.add(place)
        places.append(place)
    db.session.flush()
    return places


def seed_stories(places):
    by_title = {}
    for p in places:
        by_title[p.title] = p
        by_title[p.title.split(" — ")[0]] = p

    for raw in seed_data.STORIES:
        if raw["id"] not in CURATED_STORIES:
            continue
        place = by_title.get(raw.get("place", ""))
        slug = raw["id"]
        name_en = raw["title"]
        image = _resolve_image(
            raw.get("image"), slug, raw.get("category", "Stories & Legends"), "", name_en, ""
        )
        story = Story(
            slug=slug,
            title=raw["title"],
            excerpt=raw["excerpt"],
            author=raw["author"],
            role=raw["role"],
            read_minutes=raw["readMinutes"],
            date=raw["date"],
            image=image,
            governorate=raw.get("governorate", ""),
            category=raw.get("category", ""),
            content=raw.get("content", []),
            place_id=place.id if place else None,
        )
        db.session.add(story)


def run_seed(reset=False):
    """Populate the database with development content.

    Returns True if content was loaded, False if the database already had
    content and nothing changed.
    """
    if reset:
        db.drop_all()
        db.create_all()
    if _has_content() and not reset:
        return False

    users = seed_users()
    categories = seed_categories()
    places = seed_places(categories, users)
    seed_stories(places)
    db.session.commit()
    return True
