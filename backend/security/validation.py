from fastapi import HTTPException

def validate_study_question(question: str):
    if not question or len(question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question is empty")
    if len(question) > 1000:
        raise HTTPException(status_code=400, detail="Question too long")
    return question
