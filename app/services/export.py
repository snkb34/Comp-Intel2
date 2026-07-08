from __future__ import annotations
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from ..models import District, SourceDocument, ExtractionRow, Run

EXPORT_DIR = Path(__file__).resolve().parents[2] / "data" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _df_from_query(rows):
    return pd.DataFrame([r.__dict__ | {} for r in rows]).drop(columns=["_sa_instance_state"], errors="ignore")


def build_excel(db: Session) -> Path:
    path = EXPORT_DIR / "k12_compensation_export.xlsx"
    districts = _df_from_query(db.query(District).all())
    docs = _df_from_query(db.query(SourceDocument).all())
    rows = _df_from_query(db.query(ExtractionRow).all())
    runs = _df_from_query(db.query(Run).all())
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        (rows if not rows.empty else pd.DataFrame(columns=["district","state","category","possible_title","min_salary","mid_salary","max_salary","annual_amounts","raw_text","source_url"])).to_excel(writer, sheet_name="extracted_rows", index=False)
        (docs if not docs.empty else pd.DataFrame(columns=["district_id","category","source_url","status","message","file_name"])).to_excel(writer, sheet_name="source_documents", index=False)
        (districts if not districts.empty else pd.DataFrame(columns=["name","state","website","category"])).to_excel(writer, sheet_name="districts", index=False)
        (runs if not runs.empty else pd.DataFrame(columns=["status","message","started_at","finished_at"])).to_excel(writer, sheet_name="runs", index=False)
    return path
