from fastapi.testclient import TestClient

from server.config.factory import settings
from server.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app_name": settings.APP_NAME}
