import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import SessionLocal, get_db
from app.main import app
from tests.helpers import create_delivery_stack, upload_pdf_document


def test_invalid_document_upload_is_rejected(client: TestClient) -> None:
    _, _, delivery = create_delivery_stack(
        client,
        warehouse={"code": "GDN", "name": "Gdansk"},
    )

    response = client.post(
        f"/deliveries/{delivery['id']}/documents",
        files={"file": ("note.txt", b"plain text", "text/plain")},
    )
    assert response.status_code == 400


def test_document_upload_content_must_match_declared_type(client: TestClient) -> None:
    _, _, delivery = create_delivery_stack(
        client,
        warehouse={"code": "GDN", "name": "Gdansk"},
    )

    response = client.post(
        f"/deliveries/{delivery['id']}/documents",
        files={"file": ("fake.pdf", b"not a pdf", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid PDF file content."


def test_document_routes_reject_soft_deleted_parent_delivery(client: TestClient) -> None:
    _, _, delivery = create_delivery_stack(
        client,
        warehouse={"code": "DEL", "name": "Deleted"},
    )
    document = upload_pdf_document(client, delivery["id"])

    delete_delivery = client.delete(f"/deliveries/{delivery['id']}")
    assert delete_delivery.status_code == 204
    assert client.get(f"/deliveries/{delivery['id']}/documents").status_code == 404
    assert (
        client.get(f"/deliveries/{delivery['id']}/documents/{document['id']}/download").status_code
        == 404
    )
    assert (
        client.delete(f"/deliveries/{delivery['id']}/documents/{document['id']}").status_code == 404
    )


def test_document_soft_delete_keeps_blob_in_storage(client: TestClient, storage) -> None:
    _, _, delivery = create_delivery_stack(
        client,
        warehouse={"code": "RET", "name": "Retention"},
    )
    document = upload_pdf_document(client, delivery["id"])

    blob_path = next(iter(storage.files))
    response = client.delete(f"/deliveries/{delivery['id']}/documents/{document['id']}")

    assert response.status_code == 204
    assert blob_path in storage.files
    assert (
        client.get(f"/deliveries/{delivery['id']}/documents/{document['id']}/download").status_code
        == 404
    )


def test_document_upload_rate_limit_is_enforced(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(settings, "upload_rate_limit_per_minute", 1)
    monkeypatch.setattr(settings, "upload_rate_limit_window_seconds", 60)
    _, _, delivery = create_delivery_stack(
        client,
        warehouse={"code": "LIM", "name": "Limited"},
    )

    first = client.post(
        f"/deliveries/{delivery['id']}/documents",
        files={"file": ("first.pdf", b"%PDF-1.4 first", "application/pdf")},
    )
    second = client.post(
        f"/deliveries/{delivery['id']}/documents",
        files={"file": ("second.pdf", b"%PDF-1.4 second", "application/pdf")},
    )

    assert first.status_code == 201
    assert second.status_code == 429
    assert second.headers["Retry-After"]


def test_blob_is_deleted_when_upload_metadata_commit_fails(
    client: TestClient,
    storage,
) -> None:
    _, _, delivery = create_delivery_stack(
        client,
        warehouse={"code": "ERR", "name": "Failure"},
    )

    class CommitFailingSession:
        def __init__(self) -> None:
            self.session = SessionLocal()

        def __getattr__(self, name: str):
            return getattr(self.session, name)

        def commit(self) -> None:
            raise SQLAlchemyError("forced commit failure")

        def close(self) -> None:
            self.session.close()

    def failing_db():
        db = CommitFailingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = failing_db
    try:
        with pytest.raises(SQLAlchemyError):
            client.post(
                f"/deliveries/{delivery['id']}/documents",
                files={"file": ("delivery-note.pdf", b"%PDF-1.4 sample", "application/pdf")},
            )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert storage.files == {}
