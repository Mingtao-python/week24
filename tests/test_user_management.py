import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def login(username, password="123"):
    response = client.post("/api/users/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()


def headers(user):
    return {"token": user["token"]}


def test_teacher_sees_only_assigned_students():
    teacher = login("teacher")
    other_teacher = login("teacher2")
    student = login("ming")
    other_student = login("tao")
    admin = login("admin")
    assert client.get("/api/users/teacher/students", headers=headers(teacher)).json() == []
    result = client.post(f"/api/assign/{teacher['user_id']}/{student['user_id']}", headers=headers(admin))
    assert result.status_code == 200
    result = client.post(f"/api/assign/{other_teacher['user_id']}/{other_student['user_id']}", headers=headers(admin))
    assert result.status_code == 200
    response = client.get("/api/users/teacher/students", headers=headers(teacher))
    assert response.status_code == 200
    assert response.json() == [{"id": student["user_id"], "username": "ming"}]
    assert client.get(f"/api/progress/user/{other_student['user_id']}", headers=headers(teacher)).status_code == 403
    assert client.get(f"/api/studyplan/{other_student['user_id']}", headers=headers(teacher)).status_code == 403


@pytest.mark.parametrize("username", ["ming", "teacher"])
def test_only_admin_can_list_users_or_manage_accounts(username):
    account = login(username)
    target = login("tao")
    assert client.get("/api/users/", headers=headers(account)).status_code == 403
    assert client.put(f"/api/users/{target['user_id']}/password", json={"password": "changed-password"}, headers=headers(account)).status_code == 403
    assert client.put(f"/api/users/{target['user_id']}/role", json={"role": "admin"}, headers=headers(account)).status_code == 403
    assert login("tao")["role"] == "student"


def test_admin_directory_excludes_passwords_and_tokens():
    admin = login("admin")
    response = client.get("/api/users/", headers=headers(admin))
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert all(set(user) == {"id", "username", "role"} for user in response.json())


def test_admin_password_reset_changes_login_and_revokes_old_sessions():
    admin = login("admin")
    student = login("ming")
    response = client.put(f"/api/users/{student['user_id']}/password", json={"password": "new-student-password"}, headers=headers(admin))
    assert response.status_code == 200
    assert client.post("/api/users/login", json={"username": "ming", "password": "123"}).status_code == 401
    assert client.get(f"/api/progress/user/{student['user_id']}", headers=headers(student)).status_code == 401
    assert login("ming", "new-student-password")["role"] == "student"
    assert client.get("/api/users/", headers=headers(admin)).status_code == 200


@pytest.mark.parametrize("password", ["", "short", "x" * 129])
def test_admin_password_rules_reject_invalid_passwords(password):
    admin = login("admin")
    student = login("ming")
    response = client.put(f"/api/users/{student['user_id']}/password", json={"password": password}, headers=headers(admin))
    assert response.status_code == 422
    login("ming")


def test_teacher_has_read_access_but_cannot_write_or_generate():
    admin = login("admin")
    teacher = login("teacher")
    student = login("ming")
    assert client.post(f"/api/assign/{teacher['user_id']}/{student['user_id']}", headers=headers(admin)).status_code == 200
    assert client.put(f"/api/progress/user/{student['user_id']}", json={"percentage": 65}, headers=headers(student)).status_code == 200
    assert client.post(f"/api/studyplan/{student['user_id']}", json={"content": "Review algebra"}, headers=headers(student)).status_code == 200
    assert client.get(f"/api/progress/user/{student['user_id']}", headers=headers(teacher)).json()["percentage"] == 65
    assert client.get(f"/api/studyplan/{student['user_id']}", headers=headers(teacher)).json()["studyplan"] == "Review algebra"
    assert client.put(f"/api/progress/user/{student['user_id']}", json={"percentage": 90}, headers=headers(teacher)).status_code == 403
    assert client.post(f"/api/studyplan/{student['user_id']}", json={"content": "Changed"}, headers=headers(teacher)).status_code == 403
    assert client.post("/api/model/generate", json={"prompt": "study plan"}, headers=headers(teacher)).status_code == 403


def test_unauthenticated_account_management_is_rejected():
    assert client.get("/api/users/").status_code == 401
    assert client.get("/api/users/teacher/students").status_code == 401
    assert client.put("/api/users/1/password", json={"password": "new-password"}).status_code == 401
    assert client.put("/api/users/1/role", json={"role": "admin"}).status_code == 401
