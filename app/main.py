from fastapi import FastAPI
from .routes.auth import router as auth_router
from .routes.job_applications import router as job_applications_router

app = FastAPI( title="Job Application Tracker")

app.include_router(auth_router)

app.include_router(job_applications_router)

@app.get("/")
def  home():
    return {"message": "Welcome to Job Application Tracker"}