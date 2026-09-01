# tests/test_rate_limit.py

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def login(username, password):
    r = client.post("/api/users/login", json={"username": username, "password": password})
    return r.json()["token"]

def test_rate_limit():
    token = login("ming", "123")

    # 前 20 次不应该 429
    for i in range(20):
        r = client.get("/api/studyplan/1", headers={"token": token})
        assert r.status_code != 429

    # 第 21 次必须 429
    r = client.get("/api/studyplan/1", headers={"token": token})
    assert r.status_code == 429
