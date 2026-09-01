from fastapi import HTTPException, Header
from backend.utils.tokens import get_user_from_token
from backend.database import get_db # pyright: ignore[reportAttributeAccessIssue]

def authenticate(token: str = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    user_id = get_user_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="User not found")

    return {"id": row[0], "username": row[1], "role": row[2]}
