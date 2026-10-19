from fastapi import APIRouter, Depends, HTTPException
from backend.auth import authenticate
from backend.permissions import require_role
from backend.database import get_db
router = APIRouter()

@router.post("/assign/{teacher_id}/{student_id}")
def assign_student(
    teacher_id: int,
    student_id: int,
    user=Depends(authenticate),
):
    require_role(user, ["admin"])

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE id=?", (teacher_id,))
    teacher = cur.fetchone()
    cur.execute("SELECT role FROM users WHERE id=?", (student_id,))
    student = cur.fetchone()
    if not teacher or not student:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    if teacher[0] != "teacher" or student[0] != "student":
        conn.close()
        raise HTTPException(status_code=400, detail="Teacher and student roles required")

    cur.execute(
        "SELECT 1 FROM teacher_students WHERE teacher_id=? AND student_id=?",
        (teacher_id, student_id)
    )
    if cur.fetchone():
        conn.close()
        return {"message": "Student assigned to teacher"}

    cur.execute(
        "INSERT INTO teacher_students (teacher_id, student_id) VALUES (?, ?)",
        (teacher_id, student_id)
    )
    conn.commit()
    conn.close()

    return {"message": "Student assigned to teacher"}
