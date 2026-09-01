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
- **Ratings & reviews** — signed-in visitors rate places (1–5 stars) and leave short
  reviews on each place page. One review per person (edit or remove it anytime);
  averages and counts stay in sync automatically and feed the cards, sorting,
  and "highest rated" ordering everywhere.
- **Richer contributions** — creators and admins edit existing records directly
  (text, category, location, photos). Photo uploads carry captions, which show in
  the public gallery and admin review screens. Pending submissions are open for
  community endorsements on `/community-review` — one vote per person, toggleable —
  and reviewers see the endorsement counts.
- **Better maps** — the map clusters nearby markers into numbered bubbles at low
  zooms (expanding as you zoom in), a locate control shows your position with a
  "distance from you" line in every popup plus a nearest-records panel, and an
  offline banner appears if map tiles can't load while pins keep working.
- **Community profiles** — contributor profiles with bio and level, a gamified badge
  system (8 achievement badges), a reputation score with progress bar, and public
  contributor pages at `/contributor/<username>`. Place cards and detail pages link
  to the contributor who documented them.
- **Seed content** — a curated catalogue of 28 heritage places across 13
  governorates and all 8 categories (7 with real photographs, the rest with
  generated covers), 9 linked stories, community reviews, plus categories and
  development users.

### Tech stack

- Python 3.8+, Flask 3.0
- SQLAlchemy 2.0 + Flask-SQLAlchemy (SQLite in development, PostgreSQL-ready)
- Flask-Migrate for schema migrations, Flask-Login for sessions, Flask-Mail for emails
- Pillow for image validation, pytest for the test suite (108 passing)

## Features

- **In-app notifications** — bell icon with unread badge, dropdown preview, paginated notifications page, mark-as-read.
- **Email delivery** — optional SMTP emails via Flask-Mail (suppressed by default in dev; set `MAIL_SUPPRESS_SEND=false` to enable).
- **Notification triggers** — submission approved/rejected, new review, new endorsement.

## Next phases

Planned features and edits for the upcoming iterations:

- **More curated content** — replace remaining demo data with verified heritage places,
  each documented with real photos, coordinates, and sources.
- **Arabic support** — a full Arabic interface and Arabic search.
