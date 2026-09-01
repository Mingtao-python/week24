import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def login(username, password):
    r = client.post("/api/users/login", json={"username": username, "password": password})
    return r.json()["token"]

def test_malformed_input():
    token = login("ming", "123")

    # Missing percentage field
    r = client.put("/api/progress/1", json={}, headers={"token": token})
    assert r.status_code == 422  # FastAPI validation error

def test_access_without_auth():
    r = client.get("/api/progress/1")
    assert r.status_code == 401
