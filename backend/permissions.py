from fastapi import HTTPException
from backend.database import get_db

def authorize(
    user: dict,
    action: str,
    resource_owner_id: int | None = None,
):
    role = user["role"]

    if role == "admin":
        return

    if role == "student":
        if resource_owner_id is None or user["id"] != resource_owner_id:
            raise HTTPException(status_code=403, detail="Not your resource")
        return

    if role == "teacher":
        if resource_owner_id is None:
            raise HTTPException(status_code=403, detail="Teacher cannot access this resource")

        from backend.permissions import is_assigned_teacher
        if not is_assigned_teacher(user["id"], resource_owner_id):
            raise HTTPException(status_code=403, detail="Student not assigned to this teacher")
        return

    raise HTTPException(status_code=403, detail="Role not allowed")

def is_assigned_teacher(teacher_id: int, student_id: int) -> bool:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM teacher_students WHERE teacher_id=? AND student_id=?",
        (teacher_id, student_id)
    )
    row = cur.fetchone()
    conn.close()
    return row is not None

def require_role(user, allowed_roles):
    if user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Forbidden")

def require_owner(user, owner_id):
    if user["id"] != owner_id:
        raise HTTPException(status_code=403, detail="Not your resource")
