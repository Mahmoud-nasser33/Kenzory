# Kenzory
<img width="150" height="150" alt="kenzory-logo" src="https://github.com/user-attachments/assets/a3fb1b19-8b69-4897-ab80-ef4e25e9a07f" />

A community heritage map of Egypt. Register, add a heritage place with photos and description, and see it on the map once an admin approves it.

## What's built

- Discovery with search, filters (category, governorate, period), and pagination
- Leaflet map with clustering, locate control, and distance display
- Heritage place pages with gallery, key facts, timeline, and sources
- Long-form heritage stories
- Submit new places (title, category, location, photos)
- Admin moderation (approve/reject with notes)
- Ratings & reviews (1–5 stars, one per user per place)
- Community endorsements on pending submissions
- User profiles with bio, level, and achievement badges
- Dark mode toggle (follows system theme by default)
- In-app notifications with email delivery (Flask-Mail)
- Password reset via email
- Public JSON API at `/api`

## Tech

- Python 3.8+ / Flask 3.0
- SQLAlchemy 2.0 + SQLite (PostgreSQL-ready)
- Flask-Migrate, Flask-Login, Flask-Mail
- Pillow for image validation, pytest for tests

## API

All endpoints are GET, no auth required.

| Endpoint | Description |
| --- | --- |
| `/api/places` | List places with search & filters |
| `/api/places/<slug>` | Single place by slug or id |
| `/api/stories` | List stories |
| `/api/stories/<slug>` | Single story |
| `/api/categories` | All categories with place counts |
| `/api/nearby` | Places within a radius (`lat`, `lng`, `radius` km) |
| `/api/stats` | Platform totals |

## Next up

- More curated content with real photos and sources
- Arabic support
- Heritage trails (user-curated walking routes)
