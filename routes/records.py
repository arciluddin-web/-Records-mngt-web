from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Record


class RecordOut(BaseModel):
    id: int
    control_no: str
    doc_type: str
    doc_date: str
    reference_no: str
    sender: str
    subject: str
    summary: str
    original_filename: str
    file_path: str
    uploaded_at: str

    class Config:
        orm_mode = True

router = APIRouter()


class RecordCreate(BaseModel):
    doc_type: str = ""
    doc_date: str = ""
    reference_no: str = ""
    sender: str = ""
    subject: str = ""
    summary: str = ""
    original_filename: str = ""
    file_path: str = ""


class RecordUpdate(BaseModel):
    doc_type: str = ""
    doc_date: str = ""
    reference_no: str = ""
    sender: str = ""
    subject: str = ""
    summary: str = ""


def _generate_control_no(db: Session) -> str:
    year = datetime.now().year
    prefix = f"REC-{year}-"
    last = (
        db.query(Record)
        .filter(Record.control_no.like(f"{prefix}%"))
        .order_by(Record.control_no.desc())
        .first()
    )
    seq = int(last.control_no[len(prefix):]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


@router.get("/records", response_model=list[RecordOut])
def list_records(db: Session = Depends(get_db)):
    return db.query(Record).order_by(Record.id.desc()).all()


@router.post("/records", response_model=RecordOut)
def create_record(data: RecordCreate, db: Session = Depends(get_db)):
    record = Record(
        **data.dict(),
        control_no=_generate_control_no(db),
        uploaded_at=datetime.now().isoformat(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/records/{record_id}")
def update_record(record_id: int, data: RecordUpdate, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(404, "Record not found")
    for field, value in data.dict().items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(404, "Record not found")
    db.delete(record)
    db.commit()
    return {"ok": True}
