from fastapi.testclient import TestClient

from app.main import app


def test_application_startup_and_health() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_healthz_alias_for_managed_startup_probe() -> None:
    with TestClient(app) as client:
        response = client.get("/api/healthz")
    assert response.status_code == 200
    assert response.json()["service"] == "scientific-discovery-backend"