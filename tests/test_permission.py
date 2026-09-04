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

def test_assigned_teacher_can_view():
    tokenAdmin, adminId = login("admin", "123")
    tokenTeacher, teacherId = login("teacher", "123")
    tokenStudent, studentId = login("ming", "123")

    # Admin assigns teacher to student
    r = client.post(f"/api/assign/{teacherId}/{studentId}", headers={"token": tokenAdmin})
    assert r.status_code == 200

    # Teacher can now view assigned student's progress
    client.put(f"/api/progress/{studentId}", json={"percentage": 60}, headers={"token": tokenStudent})
    r = client.get(f"/api/progress/{studentId}", headers={"token": tokenTeacher})
    assert r.status_code == 200
    assert r.json()["percentage"] == 60

def test_admin_can_view_student():
    tokenAdmin, adminId = login("admin", "123")
    tokenStudent, studentId = login("ming", "123")

    # Student creates progress
    client.put(f"/api/progress/{studentId}", json={"percentage": 70}, headers={"token": tokenStudent})

    # Admin can view any student's progress
    r = client.get(f"/api/progress/{studentId}", headers={"token": tokenAdmin})
    assert r.status_code == 200
    assert r.json()["percentage"] == 70

def test_teacher_cannot_assign_student():
    tokenTeacher, teacherId = login("teacher", "123")
    tokenStudent, studentId = login("ming", "123")

    # Teacher tries to assign student → must be 403
    r = client.post(f"/api/assign/{teacherId}/{studentId}", headers={"token": tokenTeacher})
    assert r.status_code == 403

def test_student_cannot_assign_student():
    tokenStudent, studentId = login("ming", "123")
    tokenOtherStudent, otherId = login("tao", "123")

    # Student tries to assign another student → must be 403
    r = client.post(f"/api/assign/{otherId}/{studentId}", headers={"token": tokenStudent})
    assert r.status_code == 403