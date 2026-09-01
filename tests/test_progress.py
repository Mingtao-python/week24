# tests/test_progress.py

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def login(username, password):
    r = client.post("/api/users/login", json={"username": username, "password": password})
    return r.json()["token"], r.json()["user_id"]

def test_progress_update_and_read():
    token, userId = login("ming", "123")

    # 更新
    r = client.put(
        f"/api/progress/{userId}",
        json={"percentage": 70},
        headers={"token": token}
    )
    assert r.status_code == 200

    # 读取
    r = client.get(f"/api/progress/{userId}", headers={"token": token})
    assert r.status_code == 200
    assert r.json()["percentage"] == 70
