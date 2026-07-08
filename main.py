from __future__ import annotations
from datetime import datetime
from sqlalchemy import create_engine, String, Integer, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

DATABASE_URL = "sqlite:///data/k12_comp.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district: Mapped[str] = mapped_column(String(200), index=True)
    state: Mapped[str] = mapped_column(String(20), default="CO")
    category: Mapped[str] = mapped_column(String(100), default="Uncategorized")
    url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    documents: Mapped[list["Document"]] = relationship(back_populates="source")

class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(50), default="Started")
    message: Mapped[str] = mapped_column(Text, default="")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    run_id: Mapped[int | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    final_url: Mapped[str] = mapped_column(Text)
    filename: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(200), default="")
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="Downloaded")
    message: Mapped[str] = mapped_column(Text, default="")
    downloaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped[Source] = relationship(back_populates="documents")

class ExtractedRow(Base):
    __tablename__ = "extracted_rows"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    run_id: Mapped[int | None] = mapped_column(ForeignKey("runs.id"), nullable=True)
    district: Mapped[str] = mapped_column(String(200), index=True)
    state: Mapped[str] = mapped_column(String(20), default="CO")
    category: Mapped[str] = mapped_column(String(100), index=True)
    table_name: Mapped[str] = mapped_column(String(200), default="")
    row_text: Mapped[str] = mapped_column(Text, default="")
    title_guess: Mapped[str] = mapped_column(Text, default="")
    min_salary: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_salary: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
