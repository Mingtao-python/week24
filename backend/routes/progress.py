from fastapi import APIRouter, HTTPException, Depends
from backend.auth import authenticate
from backend.permissions import authorize
from backend.models import ProgressUpdate
from backend.database import get_db # pyright: ignore[reportAttributeAccessIssue]
from backend.security.validation import validate_study_question
router = APIRouter()


@router.put("/{progress_id}")
def update_progress(
    progress_id: int,
    update: ProgressUpdate,
    user=Depends(authenticate),
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id FROM progress WHERE id=?",
        (progress_id,)
    )
    row = cur.fetchone()

    if not row:
        # Create progress record if not exists
        cur.execute(
            "INSERT INTO progress (user_id, percentage) VALUES (?, ?)",
            (user["id"], 0)
        )
        conn.commit()
        progress_id = cur.lastrowid
        owner_id = user["id"]
    else:
        owner_id = row[0]
        authorize(user, action="update_progress", resource_owner_id=owner_id)

    # Validation
    percentage = update.percentage
    if percentage < 0 or percentage > 100:
        raise HTTPException(status_code=400, detail="Percentage must be 0–100")

    cur.execute(
        "UPDATE progress SET percentage=? WHERE id=?",
        (percentage, progress_id)
    )
    conn.commit()
    conn.close()

    return {"message": "Progress updated"}

@router.get("/{progress_id}")
def get_progress(
    progress_id: int,
    user=Depends(authenticate),
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, percentage FROM progress WHERE id=?",
        (progress_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Progress not found")

    owner_id = row[0]

    authorize(user, action="view_progress", resource_owner_id=owner_id)

    return {"user_id": owner_id, "percentage": row[1]}

