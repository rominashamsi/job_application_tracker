from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session


from ..database import get_db
from ..dependencies import get_current_user
from ..models import JobApplication, User
from ..schemas import JobApplicationCreate, JobApplicationResponse, JobApplicationUpdate


router = APIRouter(
    prefix="/job-applications",
    tags=["Job Applications"]
)
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
        salary=application_data.salary
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application





@router.get("/", response_model=list[JobApplicationResponse])
def get_job_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).all()

    return applications





@router.patch("/{application_id}", response_model=JobApplicationResponse)
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
        exclude_unset=True,
        exclude_none=True
    )

    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)

    return application







@router.delete(
    "/{application_id}")
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


@router.get("/{application_id}", response_model=JobApplicationResponse)
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