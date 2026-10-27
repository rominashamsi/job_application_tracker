
# Job Application Tracker

A backend application for tracking job applications, built with Python and FastAPI.

## Features

- User registration and login
- Password hashing with Argon2id
- JWT-based authentication with token expiration
- Change password functionality
- Create, retrieve, update, and delete job applications
- User-specific access control for job application records
- Job application status tracking
- Optional salary field
- Request validation using Pydantic
- Database management with PostgreSQL and SQLAlchemy
- Database migrations with Alembic
- Automated API tests using pytest

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- PyJWT
- Alembic
- pytest

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/rominashamsi/job_application_tracker.git
cd job_application_tracker
```

### 2. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: A securely generated JWT signing key

Never commit real credentials or secret keys.

### 5. Apply database migrations

```bash
python -m alembic upgrade head
```

### 6. Run the application

```bash
fastapi dev app/main.py
```

Open the API documentation at:

http://127.0.0.1:8000/docs

## Running Tests

```bash
python -m pytest -v
```
