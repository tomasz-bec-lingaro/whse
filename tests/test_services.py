import pytest
from fastapi import HTTPException

from app.domain.enums import DeliveryStatus
from app.services.delivery_status import is_transition_allowed
from app.services.documents import build_document_blob_path, sanitize_filename, validate_upload


def test_delivery_status_transitions() -> None:
    assert is_transition_allowed(DeliveryStatus.CREATED, DeliveryStatus.RECEIVED)
    assert is_transition_allowed(DeliveryStatus.CREATED, DeliveryStatus.CANCELLED)
    assert not is_transition_allowed(DeliveryStatus.RECEIVED, DeliveryStatus.CANCELLED)


def test_document_path_is_sanitized() -> None:
    assert sanitize_filename("../delivery note.pdf") == "delivery_note.pdf"
    assert build_document_blob_path(10, 5, "../delivery note.pdf") == (
        "deliveries/10/documents/5/delivery_note.pdf"
    )


def test_invalid_upload_type_is_rejected() -> None:
    with pytest.raises(HTTPException):
        validate_upload(
            filename="document.txt",
            content_type="text/plain",
            size_bytes=10,
            max_size_mb=10,
        )
