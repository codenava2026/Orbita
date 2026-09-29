from fastapi.testclient import TestClient

from app.main import app


def test_read_only_catalog_endpoints_are_exposed() -> None:
    with TestClient(app) as client:
        response = client.get("/api/catalog/datasets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)