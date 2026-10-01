from fastapi.testclient import TestClient


def test_delivery_document_happy_path(client: TestClient) -> None:
    supplier_response = client.post(
        "/suppliers",
        json={"name": "ACME Logistics", "tax_id": "PL123", "email": "ops@example.com"},
    )
    assert supplier_response.status_code == 201
    supplier_id = supplier_response.json()["id"]

    warehouse_response = client.post(
        "/warehouses",
        json={"code": "WAW-01", "name": "Warsaw Main Warehouse", "location": "Warsaw"},
    )
    assert warehouse_response.status_code == 201
    warehouse_id = warehouse_response.json()["id"]

    delivery_response = client.post(
        "/deliveries",
        json={
            "supplier_id": supplier_id,
            "warehouse_id": warehouse_id,
            "delivery_date": "2026-10-01",
            "status": "CREATED",
        },
    )
    assert delivery_response.status_code == 201
    delivery_id = delivery_response.json()["id"]

    upload_response = client.post(
        f"/deliveries/{delivery_id}/documents",
        files={"file": ("delivery-note.pdf", b"%PDF-1.4 sample", "application/pdf")},
    )
    assert upload_response.status_code == 201
    document = upload_response.json()
    assert document["blob_path"].startswith(f"deliveries/{delivery_id}/documents/")

    list_response = client.get(f"/deliveries/{delivery_id}/documents")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    download_response = client.get(f"/deliveries/{delivery_id}/documents/{document['id']}/download")
    assert download_response.status_code == 200
    assert download_response.content == b"%PDF-1.4 sample"

    status_response = client.patch(
        f"/deliveries/{delivery_id}/status",
        json={"status": "RECEIVED"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "RECEIVED"


def test_list_deliveries_is_paginated(client: TestClient) -> None:
    supplier_id = client.post("/suppliers", json={"name": "Supplier"}).json()["id"]
    warehouse_id = client.post("/warehouses", json={"code": "LDN", "name": "London"}).json()["id"]

    for day in range(1, 4):
        response = client.post(
            "/deliveries",
            json={
                "supplier_id": supplier_id,
                "warehouse_id": warehouse_id,
                "delivery_date": f"2026-10-0{day}",
            },
        )
        assert response.status_code == 201

    response = client.get("/deliveries?page=1&size=2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["size"] == 2
    assert payload["total"] == 3
    assert len(payload["items"]) == 2


def test_supplier_and_warehouse_update_delete(client: TestClient) -> None:
    supplier = client.post("/suppliers", json={"name": "Original Supplier"}).json()
    supplier_update = client.put(
        f"/suppliers/{supplier['id']}",
        json={"name": "Updated Supplier", "phone": "+48123123123"},
    )
    assert supplier_update.status_code == 200
    assert supplier_update.json()["name"] == "Updated Supplier"

    supplier_delete = client.delete(f"/suppliers/{supplier['id']}")
    assert supplier_delete.status_code == 204
    assert client.get(f"/suppliers/{supplier['id']}").status_code == 404

    warehouse = client.post(
        "/warehouses",
        json={"code": "POZ-01", "name": "Poznan Warehouse"},
    ).json()
    warehouse_update = client.put(
        f"/warehouses/{warehouse['id']}",
        json={"name": "Poznan Updated Warehouse", "location": "Poznan"},
    )
    assert warehouse_update.status_code == 200
    assert warehouse_update.json()["location"] == "Poznan"

    warehouse_delete = client.delete(f"/warehouses/{warehouse['id']}")
    assert warehouse_delete.status_code == 204
    assert client.get(f"/warehouses/{warehouse['id']}").status_code == 404


def test_invalid_delivery_status_transition_is_rejected(client: TestClient) -> None:
    supplier_id = client.post("/suppliers", json={"name": "Supplier"}).json()["id"]
    warehouse_id = client.post("/warehouses", json={"code": "WRO", "name": "Wroclaw"}).json()["id"]
    delivery_id = client.post(
        "/deliveries",
        json={
            "supplier_id": supplier_id,
            "warehouse_id": warehouse_id,
            "delivery_date": "2026-10-01",
            "status": "CREATED",
        },
    ).json()["id"]

    received = client.patch(f"/deliveries/{delivery_id}/status", json={"status": "RECEIVED"})
    assert received.status_code == 200
    rejected = client.patch(f"/deliveries/{delivery_id}/status", json={"status": "CANCELLED"})
    assert rejected.status_code == 409


def test_invalid_document_upload_is_rejected(client: TestClient) -> None:
    supplier_id = client.post("/suppliers", json={"name": "Supplier"}).json()["id"]
    warehouse_id = client.post("/warehouses", json={"code": "GDN", "name": "Gdansk"}).json()["id"]
    delivery_id = client.post(
        "/deliveries",
        json={
            "supplier_id": supplier_id,
            "warehouse_id": warehouse_id,
            "delivery_date": "2026-10-01",
        },
    ).json()["id"]

    response = client.post(
        f"/deliveries/{delivery_id}/documents",
        files={"file": ("note.txt", b"plain text", "text/plain")},
    )
    assert response.status_code == 400
