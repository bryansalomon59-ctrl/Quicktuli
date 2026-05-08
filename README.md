# QuickTuli Render Deploy

Files in this repo:

- `tuli.py`
- `requirementss.txt`
- `.gitignore`
- `README.md`

## Render Web Service settings

- Build Command: `pip install -r requirementss.txt`
- Start Command: `gunicorn tuli:app`

## Environment variables

Set this in Render:

- `SECRET_KEY`

## Notes

This app currently uses SQLite.
Do not upload local database files like `quicktuli.db`.
If you want to use a Render PostgreSQL database, the code must be updated to use `DATABASE_URL`.


1. Deploy it as-is and attach a persistent disk for SQLite.
2. Convert it to PostgreSQL if you want to use a Render Postgres database.

If you only want to get the app online quickly, the current repo files are enough for option 1.
If you want option 2, the code still needs to be updated from SQLite to PostgreSQL.
