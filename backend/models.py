from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class StudyPlan(BaseModel):
    content: str

class ProgressUpdate(BaseModel):
    percentage: int
