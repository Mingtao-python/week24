from pathlib import Path
import sys
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import studyplan, progress, users
from backend.database import init_db
from backend.security.errors import create_error_handlers
from backend.security.rate_limit import check_rate_limit
from backend.model_gateway import call_model
from backend.routes import assign
from pydantic import BaseModel
from backend.auth import authenticate
from backend.permissions import require_role
from backend.security.validation import validate_study_question
from contextlib import asynccontextmanager
class ModelRequest(BaseModel):
    prompt: str
    context: dict | None = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
app = FastAPI(title="Week24 AI Learning Platform V2", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
create_error_handlers(app)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    token = request.headers.get("token")
    if token:
        try:
            check_rate_limit(token)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return await call_next(request)
@app.post("/api/model/generate")
async def model_generate(
    payload: ModelRequest,
    user=Depends(authenticate),
):
    require_role(user, ["student", "admin"])
    prompt = validate_study_question(payload.prompt)
    context = payload.context or {}
    result = call_model(prompt, context)
    return {"model_output": result}
app.include_router(users.router, prefix="/api/users")
app.include_router(studyplan.router, prefix="/api/studyplan")
app.include_router(progress.router, prefix="/api/progress")
app.include_router(assign.router, prefix="/api")
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
@app.get("/", include_in_schema=False)
async def frontend_page():
    return FileResponse(FRONTEND_DIR / "index.html")
@app.get("/app.js", include_in_schema=False)
async def frontend_script():
    return FileResponse(FRONTEND_DIR / "app.js")
@app.get("/style.css", include_in_schema=False)
async def frontend_styles():
    return FileResponse(FRONTEND_DIR / "style.css")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
