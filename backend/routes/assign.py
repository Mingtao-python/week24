from fastapi import APIRouter, Depends, HTTPException
from backend.auth import authenticate
from backend.permissions import authorize
from backend.database import get_db # pyright: ignore[reportAttributeAccessIssue]

router = APIRouter()

@router.post("/assign/{teacher_id}/{student_id}")
def assign_student(
    teacher_id: int,
    student_id: int,
    user=Depends(authenticate),
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO teacher_students (teacher_id, student_id) VALUES (?, ?)",
        (teacher_id, student_id)
    )
    conn.commit()
    conn.close()

    return {"message": "Student assigned to teacher"}
