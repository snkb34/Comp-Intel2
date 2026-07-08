from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    state = Column(String(20), default="CO")
    website = Column(Text, nullable=False)
    category = Column(String(100), default="All")
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("SourceDocument", back_populates="district")

class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True)
    status = Column(String(40), default="created")
    message = Column(Text, default="")
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

class SourceDocument(Base):
    __tablename__ = "source_documents"
    id = Column(Integer, primary_key=True)
    district_id = Column(Integer, ForeignKey("districts.id"))
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=True)
    category = Column(String(100), default="All")
    source_url = Column(Text, nullable=False)
    file_name = Column(String(300), nullable=True)
    content_type = Column(String(150), nullable=True)
    status = Column(String(40), default="found")
    message = Column(Text, default="")
    downloaded_at = Column(DateTime, nullable=True)
    district = relationship("District", back_populates="documents")

class ExtractionRow(Base):
    __tablename__ = "extraction_rows"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("source_documents.id"))
    district = Column(String(200), nullable=False)
    state = Column(String(20), default="CO")
    category = Column(String(100), default="All")
    source_url = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    row_number = Column(Integer, nullable=True)
    raw_text = Column(Text, nullable=False)
    possible_title = Column(Text, nullable=True)
    min_salary = Column(Float, nullable=True)
    mid_salary = Column(Float, nullable=True)
    max_salary = Column(Float, nullable=True)
    annual_amounts = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
