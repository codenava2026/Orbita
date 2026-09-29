from fastapi.testclient import TestClient

from app.main import app


def test_constants_and_hydrogen_energy_endpoints() -> None:
    with TestClient(app) as client:
        constants = client.get("/api/science/constants")
        energy = client.get("/api/science/hydrogen/energy/1")
        state = client.get("/api/science/hydrogen/state/2/1/0")
    assert constants.status_code == 200
    assert constants.json()["version"]
    assert "G" in constants.json()["constants"]
    assert energy.status_code == 200
    assert energy.json()["n"] == 1
    assert energy.json()["energy_electron_volts"] < 0
    assert state.status_code == 200
    assert state.json()["total_nodes"] == 1


def test_invalid_hydrogen_state_returns_structured_error() -> None:
    with TestClient(app) as client:
        response = client.get("/api/science/hydrogen/state/2/2/0")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "scientific_validation_error"