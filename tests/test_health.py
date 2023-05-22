from fastapi.testclient import TestClient

from server.config.factory import settings
from server.main import app


def test_health():
    expected_response = {
        "app_name": settings.APP_NAME,
        "mode": "production",
        "debug": False,
    }

    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == expected_response
