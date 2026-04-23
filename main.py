import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends
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
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


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
