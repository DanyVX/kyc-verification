from fastapi.testclient import TestClient

from kyc.api.main import app


def test_session_api_requires_key_and_creates_session() -> None:
    client = TestClient(app)
    assert client.post("/sessions").status_code == 422
    response = client.post("/sessions", headers={"X-API-Key": "development-client-key-change-me"})
    assert response.status_code == 200
    assert response.json()["state"] == "CREATED"
