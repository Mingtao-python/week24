# tests/test_studyplan.py

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def login(username, password):
    r = client.post("/api/users/login", json={"username": username, "password": password})
    return r.json()["token"], r.json()["user_id"]

def test_student_create_own_studyplan():
    token, user_id = login("ming", "123")
    
    r = client.post(f"/api/studyplan/{user_id}", json={"content": "My study plan"}, headers={"token": token})
    assert r.status_code == 200

def test_student_read_own_studyplan():
    token, user_id = login("ming", "123")
    
    # Create first
    client.post(f"/api/studyplan/{user_id}", json={"content": "My study plan"}, headers={"token": token})
    
    # Read own
    r = client.get(f"/api/studyplan/{user_id}", headers={"token": token})
    assert r.status_code == 200
    assert "studyplan" in r.json()

def test_student_cannot_access_other_studyplan():
    tokenA, userA = login("ming", "123")
    tokenB, userB = login("tao", "123")
    
    # A creates studyplan
    client.post(f"/api/studyplan/{userA}", json={"content": "A's plan"}, headers={"token": tokenA})
    
    # B tries to access A's studyplan → 403
    r = client.get(f"/api/studyplan/{userA}", headers={"token": tokenB})
    assert r.status_code == 403

def test_assigned_teacher_can_view_studyplan():
    tokenAdmin, adminId = login("admin", "123")
    tokenTeacher, teacherId = login("teacher", "123")
    tokenStudent, studentId = login("ming", "123")
    
    # Admin assigns teacher to student
    r = client.post(f"/api/assign/{teacherId}/{studentId}", headers={"token": tokenAdmin})
    assert r.status_code == 200
    
    # Student creates studyplan
    client.post(f"/api/studyplan/{studentId}", json={"content": "Student plan"}, headers={"token": tokenStudent})
    
    # Teacher can view assigned student's studyplan
    r = client.get(f"/api/studyplan/{studentId}", headers={"token": tokenTeacher})
    assert r.status_code == 200

def test_teacher_unassigned_cannot_view_studyplan():
    tokenTeacher, teacherId = login("teacher", "123")
    tokenStudent, studentId = login("ming", "123")
    
    # Student creates studyplan
    client.post(f"/api/studyplan/{studentId}", json={"content": "Student plan"}, headers={"token": tokenStudent})
    
    # Unassigned teacher tries to view → 403
    r = client.get(f"/api/studyplan/{studentId}", headers={"token": tokenTeacher})
    assert r.status_code == 403

def test_admin_can_view_any_studyplan():
    tokenAdmin, adminId = login("admin", "123")
    tokenStudent, studentId = login("ming", "123")
    
    # Student creates studyplan
    client.post(f"/api/studyplan/{studentId}", json={"content": "Student plan"}, headers={"token": tokenStudent})
    
    # Admin can view any studyplan
    r = client.get(f"/api/studyplan/{studentId}", headers={"token": tokenAdmin})
    assert r.status_code == 200

def test_empty_content_rejected():
    token, user_id = login("ming", "123")
    
    r = client.post(f"/api/studyplan/{user_id}", json={"content": ""}, headers={"token": token})
    assert r.status_code == 400

def test_oversized_content_rejected():
    token, user_id = login("ming", "123")
    
    large_content = "x" * 10001  # Assuming max length is 10000
    r = client.post(f"/api/studyplan/{user_id}", json={"content": large_content}, headers={"token": token})
    assert r.status_code == 400

def test_missing_token_rejected():
    token, user_id = login("ming", "123")
    
    # No token header
    r = client.post(f"/api/studyplan/{user_id}", json={"content": "My plan"})
    assert r.status_code == 401
