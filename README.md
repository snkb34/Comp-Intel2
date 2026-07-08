# K-12 Compensation Intelligence App v2

A production-style foundation for collecting, extracting, searching, and exporting K-12 compensation documents.

## What v2 includes

- FastAPI web app
- In-browser source manager: add/delete district compensation URLs
- CSV upload for district/source lists
- Direct PDF / Excel / CSV downloader
- Basic web-page discovery for salary/compensation documents
- PDF table extraction with pdfplumber
- Excel and CSV extraction with pandas
- SQLite database for sources, runs, documents, and extracted rows
- Search page
- Downloadable Excel export
- Render-ready deployment files

## Render settings

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Environment variable:

```text
PYTHON_VERSION=3.12.7
```

## CSV format

```csv
district,state,website,category
Jeffco,CO,https://example.com/salary-schedule.pdf,Licensed
```

## Important note

This version performs first-pass extraction. Salary schedules vary widely by district. Some PDFs may require specialized parsing rules. The app stores raw extracted rows so you can review what was found and export it to Excel.
