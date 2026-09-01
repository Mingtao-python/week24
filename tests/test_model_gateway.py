# tests/test_model_gateway.py

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def login(username, password):
    r = client.post("/api/users/login", json={"username": username, "password": password})
    return r.json()["token"]

def test_model_requires_auth():
    r = client.post("/api/model/generate", json={"prompt": "study plan"})
    assert r.status_code == 401

def test_model_valid_input():
    token = login("ming", "123")
    r = client.post(
        "/api/model/generate",
        json={"prompt": "study plan for math", "context": {}},
        headers={"token": token}
    )
    assert r.status_code == 200
    assert "model_output" in r.json()

def test_model_rejects_empty():
    token = login("ming", "123")
    r = client.post(
        "/api/model/generate",
        json={"prompt": "   ", "context": {}},
        headers={"token": token}
    )
    assert r.status_code == 400
