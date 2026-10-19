from fastapi import APIRouter, HTTPException, Depends
from backend.models import UserLogin, PasswordChange, RoleChange
from backend.auth import authenticate
from backend.permissions import require_role, is_assigned_teacher
from backend.utils.tokens import tokens
from backend.database import get_db # pyright: ignore[reportAttributeAccessIssue]
from backend.utils.hashing import hash_password
from backend.utils.tokens import generate_token
router = APIRouter()
@router.post("/register")
def register(user: UserLogin):
    conn = get_db()
    cur = conn.cursor()
    hashed = hash_password(user.password)
    try:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (user.username, hashed, "student")
        )
        conn.commit()
    except Exception:
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")
    conn.close()
    return {"message": "User registered"}
@router.post("/login")
def login(user: UserLogin):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, password, role FROM users WHERE username=?",
        (user.username,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    stored_hash = row[1]
    if stored_hash != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = generate_token(row[0])
    return {"token": token, "user_id": row[0], "username": user.username, "role": row[2]}
@router.get("/teacher/students")
def teacher_students(user=Depends(authenticate)):
    require_role(user, ["teacher"])
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT users.id, users.username
               FROM users JOIN teacher_students
                 ON teacher_students.student_id = users.id
               WHERE teacher_students.teacher_id=? AND users.role='student'
               ORDER BY users.username""",
            (user["id"],)
        ).fetchall()
    finally:
        conn.close()
    return [{"id": row[0], "username": row[1]} for row in rows]
@router.get("/")
def list_users(user=Depends(authenticate)):
    require_role(user, ["admin"])
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, username, role FROM users ORDER BY role, username"
        ).fetchall()
    finally:
        conn.close()
    return [{"id": row[0], "username": row[1], "role": row[2]} for row in rows]
@router.put("/{user_id}/role")
def change_user_role(user_id: int, change: RoleChange, user=Depends(authenticate)):
    require_role(user, ["admin"])
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE id=?", (user_id,))
        target = cur.fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        if target[0] == "admin" and change.role != "admin":
            admins = conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
            if admins <= 1:
                raise HTTPException(status_code=400, detail="Keep at least one admin account")
        cur.execute("UPDATE users SET role=? WHERE id=?", (change.role, user_id))
        conn.commit()
    finally:
        conn.close()
    return {"message": "Role updated"}
@router.put("/{user_id}/password")
def reset_user_password(user_id: int, change: PasswordChange, user=Depends(authenticate)):
    require_role(user, ["admin"])
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET password=? WHERE id=?", (hash_password(change.password), user_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
    finally:
        conn.close()
    # Force the user to sign in again with the new password.
    for token, token_user_id in list(tokens.items()):
        if token_user_id == user_id:
            tokens.pop(token, None)
    return {"message": "Password updated. The user must log in again."}
