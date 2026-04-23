from sqlalchemy import Column, Integer, String, Text
from database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    control_no = Column(String, unique=True, index=True)
    doc_type = Column(String, default="")
    doc_date = Column(String, default="")
    reference_no = Column(String, default="")
    sender = Column(String, default="")
    subject = Column(Text, default="")
    summary = Column(Text, default="")
    original_filename = Column(String, default="")
    file_path = Column(String, default="")
    uploaded_at = Column(String, default="")
