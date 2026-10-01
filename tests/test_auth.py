from fastapi.testclient import TestClient

from app.core.config import settings


def test_non_health_endpoints_require_authentication(anonymous_client: TestClient) -> None:
    response = anonymous_client.post("/suppliers", json={"name": "ACME Logistics"})

    assert response.status_code == 401


def test_invalid_api_key_is_rejected(anonymous_client: TestClient) -> None:
    response = anonymous_client.post(
        "/suppliers",
        headers={"X-API-Key": "wrong-key"},
        json={"name": "ACME Logistics"},
    )

    assert response.status_code == 401


def test_operator_role_is_required(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key_roles", "whs:viewer")

    response = client.get("/suppliers")

    assert response.status_code == 403
