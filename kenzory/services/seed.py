"""Development seed loader.

Loads realistic Egyptian heritage content from ``kenzory.seed_data`` into the
database. This runs only on demand via ``flask seed`` and is intentionally
separate from application logic and production data.
"""

import hashlib
import os
from datetime import datetime, timedelta

from flask import current_app

from kenzory import seed_data
from kenzory.extensions import db
from kenzory.models import Category, HeritagePlace, Review, Story, User
from kenzory.services.covers import ensure_cover
from kenzory.services.reviews import recompute_all_ratings

DEV_PASSWORD = os.getenv("KENZORY_SEED_PASSWORD", "Kenzory123!")
ADMIN_PASSWORD = os.getenv("KENZORY_ADMIN_PASSWORD", "Admin123!")

# Curated content for the demo build: the full verified heritage catalogue.
# Every place has real coordinates, sources and editorial detail. Records with
# a real photograph in static/img show it; the rest use a generated cover.
CURATED_PLACES = {
    "deir-al-qusayr",
    "mosque-al-hamawi",
    "nubian-village",
    "satis-palace",
    "station-deir-sharaf",
    "temple-of-nefertari",
    "beni-hasan",
    "speos-artemidos",
    "tuna-el-gebel",
    "deir-el-medina",
    "madinet-madi",
    "qasr-el-sagha",
    "meidum",
    "deir-el-muharraq",
    "wadi-natrun",
    "al-qasr-dakhla",
    "hibis-temple",
    "kom-el-shoqafa",
    "pompeys-pillar",
    "gayer-anderson",
    "sultan-hassan",
    "shali-siwa",
    "gebel-el-silsila",
    "el-kab",
    "bab-zuweila",
    "khayamiya-street",
    "fishawy-cafe",
    "white-desert",
}

CURATED_STORIES = {
    "mosque-village-forgot",
    "tentmakers-needle",
    "salt-city",
    "door-without-a-room",
    "saving-the-sand-ship",
    "second-life-village",
    "incorrupt-bishop",
    "ghost-station-clock",
    "needle-mirrors-fishawy",
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
    bios = {
        "mahmoud": "Cairo-based editor and contributor. I document the places the guidebooks skip.",
        "dina": "I explore Upper Egypt's hidden monasteries and craft workshops.",
        "omar": "Alexandria native covering Delta architecture and Ottoman heritage.",
        "laila": "Photographer documenting Egypt's natural heritage and rock-cut temples.",
        "karim": "Railway enthusiast and heritage station hunter.",
        "youssef": "Pharaonic specialist with a focus on Middle Kingdom sites.",
        "sara": "Desert heritage researcher covering the Western Oasis.",
        "mostafa": "Cairo's old city — its crafts, cafes, and gates.",
        "hana": "Food and culture contributor from the Nile Delta.",
        "mariam": "Coptic heritage and monastic tradition researcher.",
        "norhan": "Traditional crafts and living heritage documentarian.",
        "khalid": "Southern Upper Egypt heritage guide and contributor.",
    }
    for username, meta in seed_data.CONTRIBUTORS.items():
        user = User(
            username=username,
            email=f"{username}@kenzory.example",
            display_name=meta["name"],
            bio=bios.get(username, ""),
            level=meta.get("level", "Contributor"),
            role="user",
        )
        user.set_password(DEV_PASSWORD)
        db.session.add(user)
        users.append(user)

    admin = User(
        username="admin",
        email="admin@kenzory.example",
        display_name="Kenzory Admin",
        bio="Platform administrator and editor.",
        level="Heritage Guardian",
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


def seed_reviews(places, users):
    """Deterministic community reviews backing the seeded rating aggregates.

    Star ratings jitter around each place's intended rating so recomputed
    averages land close to the curated value, and every displayed count is a
    real row in the reviews table.
    """
    bodies = [
        "A magical spot — well worth the detour.",
        "The keeper showed us around. Unforgettable hospitality.",
        "Quiet at sunrise; go early and you'll have it to yourself.",
        "One of my favourite finds this year.",
        "Needs some restoration, but the history is palpable.",
        "The kids loved it — an easy visit, under an hour.",
        "Photos don't do it justice.",
        "A real piece of living local heritage.",
        "Small site, but rich in stories.",
        "Signage is lacking, so ask locals for directions.",
        "The kind of place that makes you look twice at your own city.",
        "Peaceful, atmospheric, and completely unspoilt.",
    ]

    def h(*parts):
        digest = hashlib.md5(":".join(parts).encode("utf-8")).hexdigest()
        return int(digest, 16)

    usernames = [u for u in users if u != "admin"]
    for place in places:
        raw = next((p for p in seed_data.PLACES if p["id"] == place.slug), {})
        target = float(raw.get("rating", 4.0) or 4.0)
        base = max(1, min(5, int(round(target))))

        reviewer_count = 4 + h(place.slug, "n") % 8
        chosen = sorted(usernames, key=lambda name: h(place.slug, name))[:reviewer_count]

        for username in chosen:
            roll = h(place.slug, username) % 10
            if roll < 2:
                stars = base - 1
            elif roll < 8:
                stars = base
            else:
                stars = base + 1
            stars = max(1, min(5, stars))

            body = ""
            if h(place.slug, username, "b") % 3 != 0:
                body = bodies[h(place.slug, username, "t") % len(bodies)]

            created_at = datetime.utcnow() - timedelta(
                days=5 + h(place.slug, username, "d") % 120,
                hours=h(place.slug, username, "h") % 24,
            )
            db.session.add(
                Review(
                    place_id=place.id,
                    user_id=users[username].id,
                    rating=stars,
                    body=body,
                    created_at=created_at,
                    updated_at=created_at,
                )
            )
    db.session.flush()
    recompute_all_ratings()


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
    seed_reviews(places, users)
    db.session.commit()
    return True
