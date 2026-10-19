from fastapi import APIRouter, HTTPException, Depends
from backend.auth import authenticate
from backend.permissions import authorize, require_role
from backend.models import ProgressUpdate
from backend.database import get_db
router = APIRouter()
@router.put("/user/{user_id}")
def update_progress(
    user_id: int,
    update: ProgressUpdate,
    user=Depends(authenticate),
):
    require_role(user, ["student", "admin"])
    authorize(user, action="update_progress", resource_owner_id=user_id)
    percentage = update.percentage
    if percentage < 0 or percentage > 100:
        raise HTTPException(status_code=400, detail="Percentage must be 0–100")
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE id=?", (user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        # 按 user_id 更新，不把 user_id 当成 progress.id
        cur.execute("SELECT id FROM progress WHERE user_id=?", (user_id,))
        if cur.fetchone():
            cur.execute(
                "UPDATE progress SET percentage=? WHERE user_id=?",
                (percentage, user_id)
            )
        else:
            cur.execute(
                "INSERT INTO progress (user_id, percentage) VALUES (?, ?)",
                (user_id, percentage)
            )
        conn.commit()
    finally:
        conn.close()
    return {"message": "Progress updated"}
@router.get("/user/{user_id}")
def get_progress(user_id: int, user=Depends(authenticate)):
    authorize(user, action="view_progress", resource_owner_id=user_id)
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT percentage FROM progress WHERE user_id=? ORDER BY id DESC LIMIT 1",
            (user_id,)
        )
        row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Progress not found")
    return {"user_id": user_id, "percentage": row[0]}
