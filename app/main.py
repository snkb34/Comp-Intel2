from __future__ import annotations
from pathlib import Path
import csv
import io
from fastapi import FastAPI, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import District, SourceDocument, ExtractionRow, Run
from .services.pipeline import run_update
from .services.export import build_excel

APP_VERSION = "K-12 Compensation Intelligence v0.1.0"
Base.metadata.create_all(bind=engine)

app = FastAPI(title="K-12 Compensation Intelligence")
ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    districts = db.query(District).order_by(District.name, District.category).all()
    docs = db.query(SourceDocument).order_by(SourceDocument.id.desc()).limit(50).all()
    rows_count = db.query(ExtractionRow).count()
    runs = db.query(Run).order_by(Run.id.desc()).limit(5).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "version": APP_VERSION, "districts": districts, "docs": docs, "rows_count": rows_count, "runs": runs})

@app.post("/districts/add")
def add_district(name: str = Form(...), state: str = Form("CO"), website: str = Form(...), category: str = Form("All"), db: Session = Depends(get_db)):
    db.add(District(name=name.strip(), state=state.strip() or "CO", website=website.strip(), category=category.strip() or "All"))
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/districts/upload")
async def upload_districts(file: UploadFile = File(...), replace: bool = Form(False), db: Session = Depends(get_db)):
    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if replace:
        db.query(District).delete()
    for row in reader:
        name = row.get("District") or row.get("district") or row.get("name")
        website = row.get("Website") or row.get("website") or row.get("url")
        if not name or not website:
            continue
        db.add(District(name=name.strip(), state=(row.get("State") or row.get("state") or "CO").strip(), website=website.strip(), category=(row.get("Category") or row.get("category") or "All").strip() or "All"))
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/run")
def run_scraper(db: Session = Depends(get_db)):
    run_update(db)
    return RedirectResponse("/", status_code=303)

@app.post("/clear-results")
def clear_results(db: Session = Depends(get_db)):
    db.query(ExtractionRow).delete()
    db.query(SourceDocument).delete()
    db.query(Run).delete()
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/export")
def export(db: Session = Depends(get_db)):
    path = build_excel(db)
    return FileResponse(path, filename="k12_compensation_export.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get("/rows", response_class=HTMLResponse)
def rows(request: Request, q: str = "", db: Session = Depends(get_db)):
    query = db.query(ExtractionRow).order_by(ExtractionRow.id.desc())
    if q:
        query = query.filter(ExtractionRow.raw_text.ilike(f"%{q}%"))
    rows = query.limit(500).all()
    return templates.TemplateResponse("rows.html", {"request": request, "rows": rows, "q": q, "version": APP_VERSION})
