from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import studyplan, progress, users
from backend.database import init_db # pyright: ignore[reportAttributeAccessIssue]
from backend.security.errors import create_error_handlers
from backend.security.rate_limit import check_rate_limit
from backend.model_gateway import call_model
from backend.routes import assign
from pydantic import BaseModel
from backend.auth import authenticate
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
    allow_origins=["http://localhost:3000"],  # 后面前端模块会用
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_error_handlers(app)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    from starlette.responses import Response
    from fastapi import HTTPException
    token = request.headers.get("token")
    if token:
        try:
            check_rate_limit(token)
        except HTTPException as e:
            return Response(content=e.detail, status_code=e.status_code)
    return await call_next(request)

@app.post("/api/model/generate")
async def model_generate(
    payload: ModelRequest,
    user=Depends(authenticate),
):
    prompt = validate_study_question(payload.prompt)
    context = payload.context or {}
    result = call_model(prompt, context)
    return {"model_output": result}

app.include_router(users.router, prefix="/api/users")
app.include_router(studyplan.router, prefix="/api/studyplan")
app.include_router(progress.router, prefix="/api/progress")
app.include_router(assign.router, prefix="/api")