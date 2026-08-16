# Kenzory
<img width="150" height="150" alt="kenzory-logo" src="https://github.com/user-attachments/assets/a3fb1b19-8b69-4897-ab80-ef4e25e9a07f" />

A community heritage map of Egypt. Anyone can register, add a heritage place with a
description and photos, and see it live on the map once an admin approves it.

Built as a real, data-driven Flask application (SQLAlchemy-backed) — not a static
prototype.

## Current state

What's in the project today:

- **Discovery** — search, category chips, governorate / period filters, sorting, and
  pagination on `/explore`, plus a Leaflet map on `/map` with category filtering.
- **Stories** — long-form heritage articles written by contributors.
- **Contribution flow** — signed-in users submit new places (title, summary, category,
  location, photos). Submissions wait for moderation.
- **Moderation** — an admin dashboard to approve or reject submissions with a review
  note. Approved submissions become live places with a unique slug.
- **Auth & accounts** — register/login (username or email), password hashing, protected
  routes, open-redirect and CSRF protection. Profiles, saved places, and own
  submissions with status badges.
- **Seed content** — a curated set of 7 real heritage places (each with a genuine
  photograph) and 4 stories, plus categories and development users.

### Tech stack

- Python 3.8+, Flask 3.0
- SQLAlchemy 2.0 + Flask-SQLAlchemy (SQLite in development, PostgreSQL-ready)
- Flask-Migrate for schema migrations, Flask-Login for sessions
- Pillow for image validation, pytest for the test suite (41 passing)

## Next phases

Planned features and edits for the upcoming iterations:

- **More curated content** — replace remaining demo data with verified heritage places,
  each documented with real photos, coordinates, and sources.
- **Ratings & reviews** — let visitors rate places and leave short reviews.
- **Richer contributions** — edit existing places, upload multiple photos with captions,
  and let the community vote on pending submissions.
- **Arabic support** — a full Arabic interface and Arabic search.
- **Better maps** — marker clustering, distance-from-you, and offline-friendly tiles.
- **Notifications** — emails when a submission is approved or a story is published.
- **Community** — contributor profiles with activity and achievement badges.
