from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import District, Run, SourceDocument, ExtractionRow
from .discovery import discover_documents
from .downloader import download
from .extract import extract_rows


def run_update(db: Session) -> Run:
    run = Run(status="running", message="Starting update")
    db.add(run)
    db.commit()
    db.refresh(run)
    total_docs = 0
    total_rows = 0
    districts = db.query(District).order_by(District.name).all()
    try:
        for district in districts:
            found = discover_documents(district.website)
            if not found:
                doc = SourceDocument(district_id=district.id, run_id=run.id, category=district.category, source_url=district.website, status="not_found", message="No likely document links found")
                db.add(doc); db.commit()
                continue
            for item in found:
                doc = SourceDocument(district_id=district.id, run_id=run.id, category=district.category, source_url=item.url, content_type=item.content_type, status="found", message=item.reason)
                db.add(doc); db.commit(); db.refresh(doc)
                try:
                    file_path, ctype = download(item.url)
                    doc.file_name = file_path.name
                    doc.content_type = ctype or item.content_type
                    doc.status = "downloaded"
                    doc.downloaded_at = datetime.utcnow()
                    db.commit()
                    total_docs += 1
                    rows = extract_rows(file_path)
                    for r in rows:
                        db.add(ExtractionRow(
                            document_id=doc.id,
                            district=district.name,
                            state=district.state,
                            category=district.category,
                            source_url=item.url,
                            **r,
                        ))
                    total_rows += len(rows)
                    doc.status = "extracted" if rows else "no_rows"
                    doc.message = f"Extracted {len(rows)} rows" if rows else "Downloaded but no table/text rows were extracted"
                    db.commit()
                except Exception as exc:
                    doc.status = "error"
                    doc.message = str(exc)[:1000]
                    db.commit()
        run.status = "completed"
        run.message = f"Completed. Downloaded {total_docs} documents and extracted {total_rows} rows."
    except Exception as exc:
        run.status = "error"
        run.message = str(exc)[:1000]
    run.finished_at = datetime.utcnow()
    db.commit()
    return run
