# tests/test_rate_limit.py

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def login(username, password):
    r = client.post("/api/users/login", json={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["token"]

def test_rate_limit():
    token = login("ming", "123")

    user_id = client.post("/api/users/login", json={"username": "ming", "password": "123"}).json()["user_id"]
    r = client.post(f"/api/studyplan/{user_id}", json={"content": "Study math"}, headers={"token": token})
    assert r.status_code == 200
    from backend.security.rate_limit import requests_log
    requests_log.clear()

    # 前 20 次必须成功
    for i in range(20):
        r = client.get("/api/studyplan/1", headers={"token": token})
        assert r.status_code == 200

    # 第 21 次必须 429
    r = client.get("/api/studyplan/1", headers={"token": token})
    assert r.status_code == 429
