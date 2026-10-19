# tests/test_progress.py

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def login(username, password):
    r = client.post("/api/users/login", json={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["token"], r.json()["user_id"]

def test_progress_update_and_read():
    token, userId = login("ming", "123")

    # 更新
    r = client.put(
        f"/api/progress/user/{userId}",
        json={"percentage": 70},
        headers={"token": token}
    )
    assert r.status_code == 200

    # 读取
    r = client.get(f"/api/progress/user/{userId}", headers={"token": token})
    assert r.status_code == 200
    assert r.json()["percentage"] == 70


import pytest
from backend.database import get_db


def test_progress_uses_user_id_not_record_id():
    token, user_id = login("tao", "123")
    conn = get_db()
    conn.execute("INSERT INTO progress (id, user_id, percentage) VALUES (?, ?, ?)", (999, user_id, 10))
    conn.commit()
    conn.close()
    r = client.put(f"/api/progress/user/{user_id}", json={"percentage": 80}, headers={"token": token})
    assert r.status_code == 200
    r = client.get(f"/api/progress/user/{user_id}", headers={"token": token})
    assert r.status_code == 200
    assert r.json() == {"user_id": user_id, "percentage": 80}
    conn = get_db()
    assert conn.execute("SELECT id, percentage FROM progress WHERE user_id=?", (user_id,)).fetchall() == [(999, 80)]
    conn.close()


@pytest.mark.parametrize("percentage", [-1, 101])
def test_invalid_progress_does_not_create_record(percentage):
    token, user_id = login("ming", "123")
    r = client.put(f"/api/progress/user/{user_id}", json={"percentage": percentage}, headers={"token": token})
    assert r.status_code == 400
    conn = get_db()
    assert conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0] == 0
    conn.close()


def test_missing_user_does_not_create_progress():
    token, user_id = login("admin", "123")
    r = client.put("/api/progress/user/999", json={"percentage": 50}, headers={"token": token})
    assert r.status_code == 404
    conn = get_db()
    assert conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0] == 0
    conn.close()


def test_student_cannot_create_other_progress():
    token, user_id = login("ming", "123")
    other_token, other_id = login("tao", "123")
    r = client.put(f"/api/progress/user/{other_id}", json={"percentage": 50}, headers={"token": token})
    assert r.status_code == 403


def test_legacy_progress_url_is_not_supported():
    token, user_id = login("ming", "123")
    r = client.put("/api/progress/999", json={"percentage": 50}, headers={"token": token})
    assert r.status_code == 404
    conn = get_db()
    assert conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0] == 0
    conn.close()
