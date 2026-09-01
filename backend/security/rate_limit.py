import time
from fastapi import HTTPException

# 简单内存限流：token → [timestamps]
requests_log = {}

MAX_REQUESTS = 20
WINDOW_SECONDS = 60

def check_rate_limit(token: str):
    now = time.time()
    if token not in requests_log:
        requests_log[token] = []
    requests_log[token] = [t for t in requests_log[token] if now - t < WINDOW_SECONDS]
    if len(requests_log[token]) >= MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests")
    requests_log[token].append(now)
