import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_db

client = TestClient(app)


def login(username):
    r = client.post("/api/users/login", json={"username": username, "password": "123"})
    assert r.status_code == 200
    return r.json()


def setup_users():
    student = login("ming")
    teacher = login("teacher")
    admin = login("admin")
    r = client.put(
        f"/api/progress/user/{student['user_id']}",
        json={"percentage": 60}, headers={"token": student["token"]}
    )
    assert r.status_code == 200
    return student, teacher, admin


@pytest.mark.parametrize("username,status", [("admin", 200), ("teacher", 403), ("ming", 403)])
def test_assignment_roles(username, status):
    student, teacher, admin = setup_users()
    user = login(username)
    r = client.post(
        f"/api/assign/{teacher['user_id']}/{student['user_id']}",
        headers={"token": user["token"]}
    )
    assert r.status_code == status
    conn = get_db()
    assert conn.execute("SELECT COUNT(*) FROM teacher_students").fetchone()[0] == (1 if status == 200 else 0)
    conn.close()


def test_assignment_requires_token():
    student, teacher, admin = setup_users()
    r = client.post(f"/api/assign/{teacher['user_id']}/{student['user_id']}")
    assert r.status_code == 401


def test_assigned_teacher_can_view_student():
    student, teacher, admin = setup_users()
    path = f"/api/assign/{teacher['user_id']}/{student['user_id']}"
    for _ in range(2):
        r = client.post(path, headers={"token": admin["token"]})
        assert r.status_code == 200
    conn = get_db()
    assert conn.execute("SELECT COUNT(*) FROM teacher_students").fetchone()[0] == 1
    conn.close()
    r = client.get(f"/api/progress/user/{student['user_id']}", headers={"token": teacher["token"]})
    assert r.status_code == 200
    assert r.json()["percentage"] == 60


def test_unassigned_teacher_cannot_view_student():
    student, teacher, admin = setup_users()
    r = client.get(f"/api/progress/user/{student['user_id']}", headers={"token": teacher["token"]})
    assert r.status_code == 403


def test_admin_can_view_student():
    student, teacher, admin = setup_users()
    r = client.get(f"/api/progress/user/{student['user_id']}", headers={"token": admin["token"]})
    assert r.status_code == 200


def test_assignment_rejects_wrong_roles():
    student, teacher, admin = setup_users()
    r = client.post(f"/api/assign/{student['user_id']}/{teacher['user_id']}", headers={"token": admin["token"]})
    assert r.status_code == 400


def test_assignment_rejects_missing_user():
    student, teacher, admin = setup_users()
    r = client.post(f"/api/assign/{teacher['user_id']}/999", headers={"token": admin["token"]})
    assert r.status_code == 404
