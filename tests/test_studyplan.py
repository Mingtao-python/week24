import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def login(username):
    r = client.post("/api/users/login", json={"username": username, "password": "123"})
    assert r.status_code == 200
    return r.json()


def create_plan():
    student = login("ming")
    r = client.post(f"/api/studyplan/{student['user_id']}", json={"content": "Study math"}, headers={"token": student["token"]})
    assert r.status_code == 200
    return student


def test_student_create_and_read_own_plan():
    student = create_plan()
    r = client.get(f"/api/studyplan/{student['user_id']}", headers={"token": student["token"]})
    assert r.status_code == 200
    assert r.json()["studyplan"] == "Study math"


@pytest.mark.parametrize("method", ["get", "post"])
def test_student_cannot_access_other_plan(method):
    student = create_plan()
    other = login("tao")
    kwargs = {"headers": {"token": other["token"]}}
    if method == "post":
        kwargs["json"] = {"content": "Changed plan"}
    r = getattr(client, method)(f"/api/studyplan/{student['user_id']}", **kwargs)
    assert r.status_code == 403


@pytest.mark.parametrize("username,assigned,status", [
    ("teacher", True, 200), ("teacher", False, 403), ("admin", False, 200)
])
def test_teacher_and_admin_read_plan(username, assigned, status):
    student = create_plan()
    reader = login(username)
    if assigned:
        admin = login("admin")
        r = client.post(f"/api/assign/{reader['user_id']}/{student['user_id']}", headers={"token": admin["token"]})
        assert r.status_code == 200
    r = client.get(f"/api/studyplan/{student['user_id']}", headers={"token": reader["token"]})
    assert r.status_code == status
    if status == 200:
        assert r.json()["studyplan"] == "Study math"


@pytest.mark.parametrize("content", ["", "   ", "a" * 1001])
def test_invalid_plan_content(content):
    student = login("ming")
    r = client.post(f"/api/studyplan/{student['user_id']}", json={"content": content}, headers={"token": student["token"]})
    assert r.status_code == 400
    r = client.get(f"/api/studyplan/{student['user_id']}", headers={"token": student["token"]})
    assert r.status_code == 404


@pytest.mark.parametrize("method", ["get", "post"])
def test_plan_requires_token(method):
    kwargs = {"json": {"content": "Study math"}} if method == "post" else {}
    r = getattr(client, method)("/api/studyplan/1", **kwargs)
    assert r.status_code == 401


def test_read_latest_plan():
    student = create_plan()
    r = client.post(f"/api/studyplan/{student['user_id']}", json={"content": "Study English"}, headers={"token": student["token"]})
    assert r.status_code == 200
    r = client.get(f"/api/studyplan/{student['user_id']}", headers={"token": student["token"]})
    assert r.status_code == 200
    assert r.json()["studyplan"] == "Study English"
