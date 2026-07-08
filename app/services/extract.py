from __future__ import annotations
from pathlib import Path
import re
import pandas as pd
import pdfplumber

MONEY_RE = re.compile(r"\$?\b\d{2,3}(?:,\d{3})+(?:\.\d{2})?\b|\$?\b\d{4,6}(?:\.\d{2})?\b")

def _money_values(text: str) -> list[float]:
    vals = []
    for m in MONEY_RE.findall(text or ""):
        try:
            v = float(m.replace("$", "").replace(",", ""))
            if v >= 1000:
                vals.append(v)
        except ValueError:
            pass
    return vals


def infer_fields(raw_text: str) -> dict:
    amounts = _money_values(raw_text)
    title = raw_text
    for amt in MONEY_RE.findall(raw_text or ""):
        title = title.replace(amt, " ")
    title = " ".join(title.split())[:250]
    result = {
        "possible_title": title or None,
        "min_salary": None,
        "mid_salary": None,
        "max_salary": None,
        "annual_amounts": ", ".join(str(int(a)) for a in amounts) if amounts else None,
    }
    if len(amounts) >= 2:
        result["min_salary"] = min(amounts)
        result["max_salary"] = max(amounts)
        result["mid_salary"] = round((min(amounts) + max(amounts)) / 2, 2)
    elif len(amounts) == 1:
        result["max_salary"] = amounts[0]
    return result


def extract_rows(file_path: Path) -> list[dict]:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf" or "pdf" in file_path.name.lower():
        return extract_pdf(file_path)
    if suffix in [".xlsx", ".xls"]:
        return extract_excel(file_path)
    if suffix == ".csv":
        return extract_csv(file_path)
    # Try PDF as fallback for resource-manager files with no extension
    try:
        return extract_pdf(file_path)
    except Exception:
        return []


def extract_pdf(file_path: Path) -> list[dict]:
    rows = []
    with pdfplumber.open(str(file_path)) as pdf:
        for p_idx, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables() or []
            for table in tables:
                for r_idx, row in enumerate(table, start=1):
                    raw = " | ".join(str(c or "").strip() for c in row).strip()
                    if raw and any(ch.isdigit() for ch in raw):
                        rows.append({"page_number": p_idx, "row_number": r_idx, "raw_text": raw, **infer_fields(raw)})
            if not tables:
                text = page.extract_text() or ""
                for r_idx, line in enumerate(text.splitlines(), start=1):
                    line = line.strip()
                    if line and any(ch.isdigit() for ch in line) and any(token in line.lower() for token in ["$", "salary", "step", "grade", "range", "annual"]):
                        rows.append({"page_number": p_idx, "row_number": r_idx, "raw_text": line, **infer_fields(line)})
    return rows


def extract_excel(file_path: Path) -> list[dict]:
    rows = []
    sheets = pd.read_excel(file_path, sheet_name=None, header=None)
    for sheet, df in sheets.items():
        df = df.dropna(how="all")
        for idx, row in df.iterrows():
            raw = " | ".join(str(x).strip() for x in row.tolist() if pd.notna(x) and str(x).strip())
            if raw and any(ch.isdigit() for ch in raw):
                rows.append({"page_number": None, "row_number": int(idx) + 1, "raw_text": f"{sheet}: {raw}", **infer_fields(raw)})
    return rows


def extract_csv(file_path: Path) -> list[dict]:
    rows = []
    try:
        df = pd.read_csv(file_path, header=None)
    except pd.errors.EmptyDataError:
        return []
    for idx, row in df.iterrows():
        raw = " | ".join(str(x).strip() for x in row.tolist() if pd.notna(x) and str(x).strip())
        if raw and any(ch.isdigit() for ch in raw):
            rows.append({"page_number": None, "row_number": int(idx) + 1, "raw_text": raw, **infer_fields(raw)})
    return rows
