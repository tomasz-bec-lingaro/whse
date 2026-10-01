from fastapi.testclient import TestClient

from tests.helpers import create_supplier, create_warehouse


def test_supplier_and_warehouse_update_delete(client: TestClient) -> None:
    supplier = create_supplier(client, name="Original Supplier")
    supplier_update = client.put(
        f"/suppliers/{supplier['id']}",
        json={"name": "Updated Supplier", "phone": "+48123123123"},
    )
    assert supplier_update.status_code == 200
    assert supplier_update.json()["name"] == "Updated Supplier"

    supplier_delete = client.delete(f"/suppliers/{supplier['id']}")
    assert supplier_delete.status_code == 204
    assert client.get(f"/suppliers/{supplier['id']}").status_code == 404

    warehouse = create_warehouse(client, code="POZ-01", name="Poznan Warehouse")
    warehouse_update = client.put(
        f"/warehouses/{warehouse['id']}",
        json={"name": "Poznan Updated Warehouse", "location": "Poznan"},
    )
    assert warehouse_update.status_code == 200
    assert warehouse_update.json()["location"] == "Poznan"

    warehouse_delete = client.delete(f"/warehouses/{warehouse['id']}")
    assert warehouse_delete.status_code == 204
    assert client.get(f"/warehouses/{warehouse['id']}").status_code == 404
