from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_homepage_and_assets():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AI Learning Platform V2" in response.text
    assert 'id="login-form"' in response.text
    for asset in ["/app.js", "/style.css"]:
        assert client.get(asset).status_code == 200


def test_frontend_mount_preserves_api_routes():
    assert client.get("/docs").status_code == 200
    assert "/api/users/login" in client.get("/openapi.json").json()["paths"]
    response = client.post("/api/users/login", json={"username": "ming", "password": "123"})
    assert response.status_code == 200
    assert response.json()["role"] == "student"
