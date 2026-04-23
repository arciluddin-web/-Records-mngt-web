import os
import shutil
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile

from extractor import extract_document_info

router = APIRouter()

DATA_DIR = os.environ.get("DATA_DIR", ".")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = (file.filename or "").lower().rsplit(".", 1)[-1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type .{ext} not supported. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_name = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, saved_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        info = extract_document_info(file_path, file.filename)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(500, f"Extraction failed: {e}")

    info["original_filename"] = file.filename
    info["file_path"] = f"uploads/{saved_name}"
    return info
