from fastapi import APIRouter, HTTPException, Depends
from backend.auth import authenticate
from backend.permissions import authorize
from backend.models import StudyPlan
from backend.database import get_db # pyright: ignore[reportAttributeAccessIssue]
from backend.security.validation import validate_study_question
router = APIRouter()

@router.post("/{user_id}")
def create_studyplan(
    user_id: int,
    plan: StudyPlan,
    user=Depends(authenticate),
):
    authorize(user, action="create_studyplan", resource_owner_id=user_id)

    # Validation
    content = validate_study_question(plan.content)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO studyplan (user_id, content) VALUES (?, ?)",
        (user_id, content)
    )
    conn.commit()
    conn.close()

    return {"message": "Study plan created"}

@router.get("/{user_id}")
def get_studyplan(
    user_id: int,
    user=Depends(authenticate),
):
    authorize(user, action="view_studyplan", resource_owner_id=user_id)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT content FROM studyplan WHERE user_id=?",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="No study plan found")

    return {"studyplan": row[0]}
