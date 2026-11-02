
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.ai import router as ai_router

from .routes.auth import router as auth_router
from .routes.job_applications import router as job_applications_router


app = FastAPI(title="Job Application Tracker")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://careertrack-frontend-3r7u.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(job_applications_router)
app.include_router(ai_router)

@app.get("/")
def home():
    return {"message": "Welcome to Job Application Tracker"}
