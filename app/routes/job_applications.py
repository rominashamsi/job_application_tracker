
from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Literal
from ..services.rag.retrieval_service import search_relevant_chunks
from ..services.rag.answer_service import generate_rag_answer
from ..database import get_db
from ..dependencies import get_current_user
from ..models import JobApplication, User
from ..schemas import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
)
from ..services.rag.document_service import replace_job_application_chunks


router = APIRouter(
    prefix="/job-applications",
    tags=["Job Applications"]
)


# CREATE JOB APPLICATION
@router.post(
    "/",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job_application(
    application_data: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_application = JobApplication(
        company=application_data.company,
        job_title=application_data.job_title,
        job_url=application_data.job_url,
        notes=application_data.notes,
        user_id=current_user.id,
        salary=application_data.salary,
        job_description=application_data.job_description
    )

    try:
        db.add(new_application)

        # Get the application ID
        db.flush()

        # Generate and save chunks and embeddings
        if (
            new_application.job_description
            and new_application.job_description.strip()
        ):
            replace_job_application_chunks(
                db=db,
                job_application_id=new_application.id,
                text=new_application.job_description
            )

        db.commit()
        db.refresh(new_application)

        return new_application

    except Exception:
        db.rollback()
        raise


# GET ALL JOB APPLICATIONS
@router.get(
    "/",
    response_model=list[JobApplicationResponse]
)
def get_job_applications(
    status: Literal["applied", "interview", "offer", "rejected"] | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    )

    if status is not None:
        query = query.filter(
            JobApplication.status == status
        )

    return query.order_by(
        JobApplication.applied_date.desc(),
        JobApplication.id.desc()
    ).all()


# UPDATE JOB APPLICATION
@router.patch(
    "/{application_id}",
    response_model=JobApplicationResponse
)
def update_job_application(
    application_id: int,
    application_data: JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )

    update_data = application_data.model_dump(
        exclude_unset=True
    )

    try:
        for field, value in update_data.items():

            # Allow clearing job_description with null.
            # Keep the previous behavior for other optional fields.
            if value is None and field != "job_description":
                continue

            setattr(application, field, value)

        # Regenerate chunks only when job_description is updated.
        if "job_description" in update_data:
            replace_job_application_chunks(
                db=db,
                job_application_id=application.id,
                text=application.job_description or ""
            )

        db.commit()
        db.refresh(application)

        return application

    except Exception:
        db.rollback()
        raise


# DELETE JOB APPLICATION
@router.delete("/{application_id}")
def delete_job_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )

    db.delete(application)
    db.commit()

    return {"message": "Deleted successfully"}




# ASK AI ABOUT A JOB APPLICATION
@router.post("/{application_id}/ask")
def ask_about_job_application(
    application_id: int,
    question: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate the question
    if not question or not question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )

    # Find the application and verify ownership
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found."
        )

    # Check if the application has a job description
    if not application.job_description or not application.job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job application has no job description."
        )

    # Step 1: Retrieve relevant chunks
    retrieved_chunks = search_relevant_chunks(
        db=db,
        job_application_id=application.id,
        query=question,
        top_k=5
    )

    # Step 2: Generate an answer using Gemini
    answer = generate_rag_answer(
        question=question,
        retrieved_chunks=retrieved_chunks
    )

    return {
        "question": question,
        "answer": answer,
        "sources": retrieved_chunks
    }







# GET ONE JOB APPLICATION
@router.get(
    "/{application_id}",
    response_model=JobApplicationResponse
)
def get_job_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )

    return application
