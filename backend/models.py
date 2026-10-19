from pydantic import BaseModel
class UserLogin(BaseModel):
    username: str
    password: str
class StudyPlan(BaseModel):
    content: str
class ProgressUpdate(BaseModel):
    percentage: int
from typing import Literal
from pydantic import Field
class PasswordChange(BaseModel):
    password: str = Field(min_length=8, max_length=128)
class RoleChange(BaseModel):
    role: Literal["student", "teacher", "admin"]
