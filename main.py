import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from auth import verify_credentials
from database import Base, engine
import models  # noqa: F401 — registers ORM models

Base.metadata.create_all(bind=engine)

from routes.export import router as export_router
from routes.records import router as records_router
from routes.upload import router as upload_router

app = FastAPI(title="FAD Records Management")

auth = [Depends(verify_credentials)]
app.include_router(upload_router, dependencies=auth)
app.include_router(records_router, dependencies=auth)
app.include_router(export_router, dependencies=auth)

UPLOAD_DIR = os.path.join(os.environ.get("DATA_DIR", "."), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/uploads/{filename}", dependencies=auth)
def get_upload(filename: str):
    # Serve uploaded files only to logged-in users, and only from UPLOAD_DIR.
    base = os.path.realpath(UPLOAD_DIR)
    path = os.path.realpath(os.path.join(base, filename))
    if os.path.dirname(path) != base or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
