import re
from pathlib import PurePath

from fastapi import HTTPException

SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
}


def sanitize_filename(filename: str) -> str:
    name = PurePath(filename).name
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return safe_name or "document"


def build_document_blob_path(delivery_id: int, document_id: int, filename: str) -> str:
    return f"deliveries/{delivery_id}/documents/{document_id}/{sanitize_filename(filename)}"


def validate_upload(
    filename: str | None,
    content_type: str | None,
    size_bytes: int,
    max_size_mb: int,
) -> None:
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required.")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and JPG files are supported.")
    if size_bytes <= 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if size_bytes > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Uploaded file is too large.")
