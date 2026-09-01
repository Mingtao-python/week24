# tests/test_auth.py

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_login_success():
    r = client.post("/api/users/login", json={"username": "ming", "password": "123"})
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert "user_id" in data

def test_login_fail_wrong_password():
    r = client.post("/api/users/login", json={"username": "ming", "password": "wrong"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid username or password"

def test_login_fail_missing_fields():
    r = client.post("/api/users/login", json={"username": "ming"})
    assert r.status_code == 400 or r.status_code == 422
