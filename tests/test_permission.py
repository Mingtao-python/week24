# tests/test_permission.py
from fastapi.testclient import TestClient
from backend.main import app
client = TestClient(app)
def login(username, password):
    r = client.post("/api/users/login", json={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["token"], r.json()["user_id"]
def test_student_cannot_access_other_student_progress():
    tokenA, userA = login("ming", "123")
    tokenB, userB = login("tao", "123")
    # A 创建自己的 progress
    created = client.put(f"/api/progress/user/{userA}", json={"percentage": 50}, headers={"token": tokenA})
    assert created.status_code == 200
    # B 访问 A 的 progress → 必须 403
    r = client.get(f"/api/progress/user/{userA}", headers={"token": tokenB})
    assert r.status_code == 403
def test_teacher_must_be_assigned():
    tokenTeacher, teacherId = login("teacher", "123")
    tokenStudent, studentId = login("ming", "123")
    # teacher 未被分配 → 必须 403
    r = client.get(f"/api/progress/user/{studentId}", headers={"token": tokenTeacher})
    assert r.status_code == 403
