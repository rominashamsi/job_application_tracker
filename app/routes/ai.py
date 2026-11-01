
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from google.genai.errors import ServerError
from pydantic import BaseModel

from ..core.ai_service import (
    generate_interview_questions,
    stream_interview_questions,
)
from ..dependencies import get_current_user
from ..models import User


router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)


class InterviewQuestionsRequest(BaseModel):
    job_title: str
    previous_questions: str | None = None


class InterviewQuestionsResponse(BaseModel):
    job_title: str
    questions: str


# Generate all questions at once
@router.post(
    "/interview-questions",
    response_model=InterviewQuestionsResponse
)
def create_interview_questions(
    request: InterviewQuestionsRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        questions = generate_interview_questions(
            request.job_title,
            request.previous_questions,
        )

    except ServerError as error:
        print(f"Gemini API error: {error}")

        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable."
        ) from error

    return InterviewQuestionsResponse(
        job_title=request.job_title,
        questions=questions
    )


# Stream interview questions gradually
@router.post("/interview-questions/stream")
def create_interview_questions_stream(
    request: InterviewQuestionsRequest,
    current_user: User = Depends(get_current_user)
):
    return StreamingResponse(
        stream_interview_questions(
            request.job_title,
            request.previous_questions,
        ),
        media_type="text/plain"
    )
