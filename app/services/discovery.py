from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re
import requests
from bs4 import BeautifulSoup

DOC_EXTENSIONS = (".pdf", ".xlsx", ".xls", ".csv")
KEYWORDS = ["salary", "salaries", "compensation", "schedule", "pay", "agreement", "licensed", "admin", "administrator", "classified"]

@dataclass
class FoundDocument:
    url: str
    content_type: str | None = None
    reason: str = ""


def looks_like_document_url(url: str) -> bool:
    lower = url.lower().split("?")[0]
    return lower.endswith(DOC_EXTENSIONS) or "/resource-manager/view/" in lower or "aptg.co" in lower


def discover_documents(start_url: str, timeout: int = 25) -> list[FoundDocument]:
    """Return direct documents. If start_url is a PDF/resource link, return it as-is.
    Otherwise, crawl only that page for likely compensation document links.
    """
    if not start_url or not start_url.strip():
        return []
    start_url = start_url.strip()
    if looks_like_document_url(start_url):
        return [FoundDocument(start_url, reason="direct_document_url")]

    headers = {"User-Agent": "K12CompIntel/1.0 (+salary schedule research)"}
    resp = requests.get(start_url, headers=headers, timeout=timeout, allow_redirects=True)
    ctype = resp.headers.get("content-type", "")
    final_url = resp.url
    if "pdf" in ctype.lower() or looks_like_document_url(final_url):
        return [FoundDocument(final_url, ctype, "resolved_to_document")]

    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    found: list[FoundDocument] = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        text = " ".join(a.get_text(" ", strip=True).split())
        full = urljoin(final_url, href)
        blob = f"{text} {full}".lower()
        if full in seen:
            continue
        if looks_like_document_url(full) or any(k in blob for k in KEYWORDS):
            seen.add(full)
            found.append(FoundDocument(full, reason=text[:200] or "matched_link"))
    return found[:25]
