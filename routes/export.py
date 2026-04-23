import io

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from sqlalchemy.orm import Session

from database import get_db
from models import Record

router = APIRouter()

COLUMNS = [
    "control_no", "doc_type", "doc_date", "reference_no",
    "sender", "subject", "summary", "original_filename", "uploaded_at",
]
HEADERS = [
    "Control No", "Type", "Date", "Ref No",
    "Sender", "Subject", "Summary", "File", "Logged At",
]


def _to_df(db: Session) -> pd.DataFrame:
    records = db.query(Record).order_by(Record.id).all()
    rows = [{col: getattr(r, col, "") or "" for col in COLUMNS} for r in records]
    return pd.DataFrame(rows, columns=COLUMNS)


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    buf = io.StringIO()
    _to_df(db).to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        buf, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=records.csv"},
    )


@router.get("/export/excel")
def export_excel(db: Session = Depends(get_db)):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        _to_df(db).to_excel(writer, index=False, sheet_name="Records")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=records.xlsx"},
    )


@router.get("/export/pdf")
def export_pdf(db: Session = Depends(get_db)):
    records = db.query(Record).order_by(Record.id).all()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20,
    )
    styles = getSampleStyleSheet()

    pdf_headers = ["Control No", "Type", "Date", "Ref No", "Sender", "Subject", "Logged"]
    data = [pdf_headers]
    for r in records:
        data.append([
            r.control_no or "",
            r.doc_type or "",
            r.doc_date or "",
            r.reference_no or "",
            (r.sender or "")[:40],
            (r.subject or "")[:60],
            (r.uploaded_at or "")[:10],
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eff6ff")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))

    title = Paragraph("FAD Records Logbook", styles["Title"])
    doc.build([title, table])
    buf.seek(0)
    return StreamingResponse(
        buf, media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=records_logbook.pdf"},
    )
