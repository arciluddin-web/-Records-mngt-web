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
