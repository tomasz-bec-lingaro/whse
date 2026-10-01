from fastapi.testclient import TestClient

from tests.helpers import create_delivery, create_supplier, create_warehouse


def test_list_deliveries_is_paginated(client: TestClient) -> None:
    supplier = create_supplier(client)
    warehouse = create_warehouse(client, code="LDN", name="London")

    for day in range(1, 4):
        create_delivery(
            client,
            supplier["id"],
            warehouse["id"],
            delivery_date=f"2026-10-0{day}",
        )

    response = client.get("/deliveries?page=1&size=2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["size"] == 2
    assert payload["total"] == 3
    assert len(payload["items"]) == 2


def test_invalid_delivery_status_transition_is_rejected(client: TestClient) -> None:
    supplier = create_supplier(client)
    warehouse = create_warehouse(client, code="WRO", name="Wroclaw")
    delivery = create_delivery(
        client,
        supplier["id"],
        warehouse["id"],
        status="CREATED",
    )

    received = client.patch(f"/deliveries/{delivery['id']}/status", json={"status": "RECEIVED"})
    assert received.status_code == 200
    rejected = client.patch(f"/deliveries/{delivery['id']}/status", json={"status": "CANCELLED"})
    assert rejected.status_code == 409
