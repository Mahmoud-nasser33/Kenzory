"""Build-time database bootstrap for Vercel deployments.

Runs schema migrations and seeds development content during the Vercel build,
but only when DATABASE_URL is configured. Without it the script is a no-op so
local builds and previews never fail on a missing database.

Run with: python vercel_build.py
"""

import os


def main():
    if not os.environ.get("DATABASE_URL"):
        print("DATABASE_URL not set — skipping database bootstrap.")
        return

    from flask_migrate import upgrade

    from app import app
    from kenzory.services.seed import run_seed

    with app.app_context():
        upgrade()
        loaded = run_seed(reset=False)
        if loaded:
            print("Database migrated and seeded with development content.")
        else:
            print("Database migrated; content already present.")


if __name__ == "__main__":
    main()
