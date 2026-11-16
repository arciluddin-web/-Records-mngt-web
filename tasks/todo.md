# FAD Records Management — Todo

## Plan
Local web app (FastAPI + SQLite + Claude API) for uploading documents, AI-extracting key fields, and managing a searchable records database.

## Checklist

- [x] Create project directory structure
- [x] Create `tasks/todo.md`
- [x] Create `requirements.txt` and install dependencies
- [x] Create `.env` with API key placeholder
- [x] Build `database.py` and `models.py`
- [x] Build `extractor.py` — Claude API extraction
- [x] Build `routes/upload.py`
- [x] Build `routes/records.py`
- [x] Build `routes/export.py`
- [x] Build `main.py`
- [x] Build `static/index.html`
- [x] Build `static/app.js`
- [x] Build `static/style.css`
- [ ] Test end-to-end (requires API key in .env)

## Review
All backend and frontend files created. App verified to import cleanly. Pending: user must add their API key to `.env`, then run `python main.py` to launch.

---

# Security fixes — uploads and credentials

## Plan
- [x] `auth.py`: stop falling back to `admin` / `changeme`; refuse to start if `APP_USERNAME` or `APP_PASSWORD` is missing, or if the password is still `changeme`
- [x] `main.py`: remove the public `/uploads` static mount
- [x] `main.py`: add `GET /uploads/{filename}` behind Basic Auth, serving only files inside the uploads folder (blocks `../` path tricks)
- [x] Test: app refuses to start without credentials; file links need a login; wrong login and `../` paths are rejected; health check still open

## Review
- `auth.py` now checks credentials once at startup. A deploy without real `APP_USERNAME` / `APP_PASSWORD` fails the Railway health check, so Railway keeps the previous version running instead of going live with default credentials.
- Uploaded files are now served by an authenticated route at the same URLs (`/uploads/<name>`), so existing links in the front end and saved records keep working. Browsers resend the Basic Auth login automatically, so logged-in users notice no change.
- No change to the front end, database, or upload flow.
