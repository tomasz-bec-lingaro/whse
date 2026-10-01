from typing import Any

from fastapi.testclient import TestClient

JsonDict = dict[str, Any]


def create_supplier(client: TestClient, **overrides: Any) -> JsonDict:
    payload = {"name": "Supplier"}
    payload.update(overrides)

    response = client.post("/suppliers", json=payload)
    assert response.status_code == 201
    return response.json()


def create_warehouse(client: TestClient, **overrides: Any) -> JsonDict:
    payload = {"code": "WHS", "name": "Warehouse"}
    payload.update(overrides)

    response = client.post("/warehouses", json=payload)
    assert response.status_code == 201
    return response.json()


def create_delivery(
    client: TestClient,
    supplier_id: int,
    warehouse_id: int,
    **overrides: Any,
) -> JsonDict:
    payload = {
        "supplier_id": supplier_id,
        "warehouse_id": warehouse_id,
        "delivery_date": "2026-10-01",
    }
    payload.update(overrides)

    response = client.post("/deliveries", json=payload)
    assert response.status_code == 201
    return response.json()


def create_delivery_stack(
    client: TestClient,
    *,
    supplier: JsonDict | None = None,
    warehouse: JsonDict | None = None,
    delivery: JsonDict | None = None,
) -> tuple[JsonDict, JsonDict, JsonDict]:
    created_supplier = create_supplier(client, **(supplier or {}))
    created_warehouse = create_warehouse(client, **(warehouse or {}))
    created_delivery = create_delivery(
        client,
        created_supplier["id"],
        created_warehouse["id"],
        **(delivery or {}),
    )
    return created_supplier, created_warehouse, created_delivery


def upload_pdf_document(
    client: TestClient,
    delivery_id: int,
    *,
    filename: str = "delivery-note.pdf",
    content: bytes = b"%PDF-1.4 sample",
) -> JsonDict:
    response = client.post(
        f"/deliveries/{delivery_id}/documents",
        files={"file": (filename, content, "application/pdf")},
    )
    assert response.status_code == 201
    return response.json()
