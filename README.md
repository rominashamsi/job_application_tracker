# CareerTrack – Job Application Tracker

[![Python Tests](https://github.com/rominashamsi/job_application_tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/rominashamsi/job_application_tracker/actions/workflows/tests.yml)

CareerTrack is a full-stack job application tracking platform built with **Python, FastAPI, Vue.js, and PostgreSQL**. It helps users organize their job applications, monitor their application progress, and prepare for interviews using an AI-powered interview assistant.



## Live Demo

The application is deployed and publicly accessible:

- **Live Application:** [CareerTrack](https://careertrack-frontend-3r7u.onrender.com)
- **Backend API:** [Backend API](https://job-application-tracker-3gwb.onrender.com)
- **API Documentation:** [Swagger UI](https://job-application-tracker-3gwb.onrender.com/docs)

## Deployment & Infrastructure

| Component | Technology / Platform |
|---|---|
| Frontend Hosting | Render |
| Backend Hosting | Render |
| Database | PostgreSQL on Neon |
| Database Migrations | Alembic |
| CI | GitHub Actions |

The frontend and backend are deployed separately on Render. The backend connects to a cloud-hosted PostgreSQL database on Neon through environment variables configured in Render.



## Features

### Job Application Management
- Create, view, update, and delete job applications.
- Track application statuses.
- Store company names, job titles, job links, notes, and optional salary information.
- Filter applications by status.
- View application statistics on the dashboard.
- User-specific access control.

### Authentication
- User registration and login.
- Password hashing with Argon2id.
- JWT-based authentication with token expiration.
- Change password functionality.

### AI Interview Assistant
- Generate role-specific interview questions using Google Gemini.
- Generate additional sets of interview questions.
- Include technical and behavioral questions.
- Stream AI-generated responses progressively to the frontend.

## Tech Stack

**Backend**
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- PyJWT
- Alembic

**Frontend**
- Vue 3
- TypeScript
- Vite
- HTML and CSS

**AI Integration**
- Google Gemini API

**Testing and CI**
- pytest
- HTTPX
- GitHub Actions

## Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/rominashamsi/job_application_tracker.git
cd job_application_tracker
```

### 2. Set up the Python environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

Configure the following variables:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/job_application_tracker
SECRET_KEY=your_secure_jwt_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder values with your own configuration.

Never commit real credentials, API keys, or secret keys to GitHub.

### 5. Run database migrations

Make sure PostgreSQL is running and the database has been created.

```bash
python -m alembic upgrade head
```

### 6. Run the backend

From the project root:

```bash
python -m uvicorn app.main:app --reload
```

Backend API:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

### 7. Run the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the frontend at:

http://localhost:5173

## Running Tests

Run the automated backend tests from the project root:

```bash
python -m pytest -v
```

AI integration tests use mocked responses, so automated tests do not require actual Gemini API requests.

GitHub Actions automatically runs the test suite when changes are pushed to the repository.

## Future Improvements

- Resume upload and parsing.
- AI-powered resume and job description matching.
- Personalized interview feedback.
- Interview history and progress tracking.

## Author

Developed as a full-stack software engineering project using Python, FastAPI, Vue.js, PostgreSQL, and Google Gemini.