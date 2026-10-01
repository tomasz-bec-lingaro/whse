from fastapi.testclient import TestClient

from tests.helpers import create_delivery, create_supplier, create_warehouse, upload_pdf_document


def test_delivery_document_happy_path(client: TestClient, storage) -> None:
    supplier = create_supplier(
        client,
        name="ACME Logistics",
        tax_id="PL123",
        email="ops@example.com",
    )
    warehouse = create_warehouse(
        client,
        code="WAW-01",
        name="Warsaw Main Warehouse",
        location="Warsaw",
    )
    delivery = create_delivery(
        client,
        supplier["id"],
        warehouse["id"],
        status="CREATED",
    )

    document = upload_pdf_document(client, delivery["id"])
    assert "blob_path" not in document

    list_response = client.get(f"/deliveries/{delivery['id']}/documents")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    download_response = client.get(
        f"/deliveries/{delivery['id']}/documents/{document['id']}/download"
    )
    assert download_response.status_code == 200
    assert download_response.content == b"%PDF-1.4 sample"
    assert storage.download_chunk_paths

    status_response = client.patch(
        f"/deliveries/{delivery['id']}/status",
        json={"status": "RECEIVED"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "RECEIVED"
