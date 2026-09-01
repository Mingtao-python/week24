# tests/test_permission.py

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def login(username, password):
    r = client.post("/api/users/login", json={"username": username, "password": password})
    return r.json()["token"], r.json()["user_id"]

def test_student_cannot_access_other_student_progress():
    tokenA, userA = login("ming", "123")
    tokenB, userB = login("tao", "123")

    # A 创建自己的 progress
    client.put(f"/api/progress/{userA}", json={"percentage": 50}, headers={"token": tokenA})

    # B 访问 A 的 progress → 必须 403
    r = client.get(f"/api/progress/{userA}", headers={"token": tokenB})
    assert r.status_code == 403

def test_teacher_must_be_assigned():
    tokenTeacher, teacherId = login("teacher", "123")
    tokenStudent, studentId = login("ming", "123")

    # teacher 未被分配 → 必须 403
    r = client.get(f"/api/progress/{studentId}", headers={"token": tokenTeacher})
    assert r.status_code == 403