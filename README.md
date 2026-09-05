# Kenzory
<img width="150" height="150" alt="kenzory-logo" src="https://github.com/user-attachments/assets/a3fb1b19-8b69-4897-ab80-ef4e25e9a07f" />

A community heritage map of Egypt. Register, add a heritage place with photos and description, and see it on the map once an admin approves it — or curate walking routes that string approved places into a guided trail.

> **Note:** The app is under testing and not finished yet, coming soon.

## What's built

- Discovery with search, filters (category, governorate, period), and pagination
- Leaflet map with clustering, locate control, and distance display
- Heritage place pages with gallery, key facts, timeline, and sources
- Long-form heritage stories
- Submit new places (title, category, location, photos)
- Admin moderation (approve/reject with notes, full admin area)
- Ratings & reviews (1–5 stars, one per user per place)
- Community endorsements on pending submissions
- **Heritage trails** — user-curated walking routes (ordered stops, duration, cover, interactive map, API)
- User profiles with bio, level, achievement badges, and contributed trails
- Dark mode toggle (follows system theme by default)
- In-app notifications with email delivery (Flask-Mail)
- Password reset via email
- Public JSON API at `/api`
- Production hardening: health check, security headers, fail-fast config, Docker + gunicorn

## Tech

- Python 3.8+ / Flask 3.0
- SQLAlchemy 2.0 + SQLite (PostgreSQL-ready)
- Flask-Migrate, Flask-Login, Flask-Mail
- Pillow for image validation, pytest for tests

## Local development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
flask db upgrade
flask seed
flask run
```

- Empty environments auto-start with nothing; `flask seed` loads the curated demo catalogue.
- `flask seed --reset` drops all tables and reseeds from scratch.
- Seeded logins: `admin / Admin123!` (change before production), dev users `<username>@kenzory.example / Kenzory123!`.

Run the test suite with `pytest` (or `python -m pytest`).

## Configuration

All settings come from environment variables (see `.env.example`):

| Variable | Purpose |
| --- | --- |
| `KENZORY_ENV` | `development` (default), `testing`, or `production` |
| `SECRET_KEY` | Session signing key — **required in production** |
| `DATABASE_URL` | SQLAlchemy URL; defaults to a local SQLite file in dev, **required in production** (e.g. `postgresql+psycopg2://...`) |
| `MAIL_*` | Flask-Mail SMTP settings for notifications and password resets |
| `KENZORY_ADMIN_PASSWORD` / `KENZORY_SEED_PASSWORD` | Seed-time credentials used only when the database is empty |

### Production

Production refuses to start without a strong `SECRET_KEY` and a `DATABASE_URL`, and defaults to HTTPS cookies.

**Docker (PostgreSQL + gunicorn):**

```bash
cp .env.example .env   # then fill in SECRET_KEY, POSTGRES_PASSWORD, MAIL_*, seed passwords
docker compose up --build
```

The container runs `flask db upgrade` and (on an empty database) `flask seed` before starting gunicorn on port 8000. `static/uploads`, `static/img/covers`, and the Postgres volume persist in Docker volumes.

**Heroku/Railway-style deploy:** `Procfile` runs gunicorn — e.g. `web: gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 60 app:app`. Set `KENZORY_ENV=production` and the required variables, then `flask db upgrade` against the provisioned database.

Health check: `GET /healthz` returns `200 {"status": "ok"}` when the database responds, `503` otherwise.

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
| `/api/trails` | List published trails |
| `/api/trails/<slug>` | Single trail with ordered stops |
| `/api/stats` | Platform totals |

## Next up

- More curated content with real photos and sources
- User-submitted trails with an admin approval flow
- Full-text search tuning and a SQLite→PostgreSQL migration guide