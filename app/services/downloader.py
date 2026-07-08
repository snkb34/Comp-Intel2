from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import mimetypes
import requests

DOWNLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def safe_name(url: str, content_type: str | None = None) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name or "document"
    if "." not in name:
        ext = mimetypes.guess_extension((content_type or '').split(';')[0].strip()) or ".bin"
        if ext == ".jpe":
            ext = ".jpg"
        name = f"document{ext}"
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    return f"{digest}_{name}".replace("/", "_")


def download(url: str, timeout: int = 45) -> tuple[Path, str | None]:
    headers = {"User-Agent": "K12CompIntel/1.0 (+salary schedule research)"}
    resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    ctype = resp.headers.get("content-type")
    file_path = DOWNLOAD_DIR / safe_name(resp.url, ctype)
    file_path.write_bytes(resp.content)
    return file_path, ctype
