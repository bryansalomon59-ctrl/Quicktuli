# QuickTuli Render Deploy

These are the files to put in your GitHub repo for Render:

- `app.py`
- `requirements.txt`
- `render.yaml`
- `.gitignore`
- `.env.example`
- `README.md`

Do not upload local database files or local app data:

- `quicktuli.db`
- `*.db-journal`
- `instance/`
- `__pycache__/`
- `.env`

## Render settings

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

## Environment variables in Render

Add this in your Render web service:

- `SECRET_KEY`

## Current database setup

This app currently uses SQLite through `instance/quicktuli.db`.

That means you have two choices on Render:

1. Deploy it as-is and attach a persistent disk for SQLite.
2. Convert it to PostgreSQL if you want to use a Render Postgres database.

If you only want to get the app online quickly, the current repo files are enough for option 1.
If you want option 2, the code still needs to be updated from SQLite to PostgreSQL.
