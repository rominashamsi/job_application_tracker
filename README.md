# CareerTrack – Job Application Tracker

[![Python Tests](https://github.com/rominashamsi/job_application_tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/rominashamsi/job_application_tracker/actions/workflows/tests.yml)

CareerTrack is a full-stack job application tracking platform built with **Python, FastAPI, Vue.js, and PostgreSQL**. It helps users organize job applications, monitor their application progress, and prepare for interviews using AI-powered features.

The platform includes an AI Interview Assistant and a Retrieval-Augmented Generation (RAG) based AI Job Assistant that answers questions using information retrieved from saved job descriptions.

## Live Demo

The application is deployed and publicly accessible:

- **Live Application:** [CareerTrack](https://careertrack-frontend-3r7u.onrender.com)
- **Backend API:** [Backend API](https://job-application-tracker-3gwb.onrender.com)
- **API Documentation:** [Swagger UI](https://job-application-tracker-3gwb.onrender.com/docs)

## Features

### Job Application Management

- Create, view, update, and delete job applications.
- Track application statuses.
- Store company names, job titles, job links, notes, job descriptions, and optional salary information.
- Filter applications by status.
- View application statistics on the dashboard.
- User-specific access control.

### Authentication

- User registration and login.
- Password hashing with Argon2id.
- JWT-based authentication with token expiration.
- Change password functionality.
- Protected API endpoints.

### AI Interview Assistant

- Generate role-specific interview questions using Google Gemini.
- Generate additional sets of interview questions.
- Include technical and behavioral questions.
- Stream AI-generated responses progressively to the frontend.

### AI Job Assistant – RAG

A Retrieval-Augmented Generation (RAG) feature that allows users to ask questions about their saved job descriptions.

**Key capabilities:**
- Save job descriptions with job applications.
- Split job descriptions into smaller text chunks.
- Generate semantic embeddings using Google's Gemini Embedding API.
- Store text chunks and vector embeddings in PostgreSQL using pgvector.
- Retrieve relevant information through semantic similarity search.
- Generate context-aware answers using Google Gemini.
- Return source text alongside AI-generated answers.
- Restrict access to job applications owned by the authenticated user.

**Example questions:**
- What programming languages are required for this position?
- What are the main responsibilities?
- Which technical skills are required?
- Does this job require Python experience?
- Is a salary range specified in the job description?

## RAG Architecture

CareerTrack uses a simple RAG pipeline without relying on frameworks such as LangChain or LlamaIndex.

### 1. Document Processing

When a user saves or updates a job description:

1. The text is split into chunks.
2. Each chunk is converted into a vector embedding.
3. The chunks and embeddings are stored in PostgreSQL.

Current chunking configuration:
- Chunk size: 200 words.
- Chunk overlap: 40 words.
- Embedding dimensions: 768.

### 2. Retrieval

When a user asks a question:

1. The question is converted into an embedding.
2. The embedding is compared with stored document embeddings.
3. Cosine distance is used to retrieve the most relevant chunks.
4. The top relevant chunks are passed to Gemini as context.

### 3. Generation

Gemini generates an answer using the retrieved job description content.

The assistant is instructed to answer using the supplied context and to state when the job description does not contain the requested information.

### RAG Workflow

```text
Job Description
       |
       v
Text Chunking
       |
       v
Gemini Embeddings
       |
       v
PostgreSQL + pgvector
       |
       | 
User Question
       |
       v
Query Embedding
       |
       v
Semantic Similarity Search
       |
       v
Relevant Text Chunks
       |
       v
Google Gemini
       |
       v
Answer + Sources
```

## API Endpoint

The RAG assistant is exposed through the following authenticated endpoint:

**POST** `/job-applications/{application_id}/ask`

Example request:

```json
{
  "question": "What programming languages are required for this position?"
}
```

Example response:

```json
{
  "question": "What programming languages are required for this position?",
  "answer": "Python is the required programming language.",
  "sources": [
    "The relevant text retrieved from the job description."
  ]
}
```

The endpoint verifies application ownership before retrieving document chunks or generating an answer.

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Pydantic
- PyJWT
- Alembic

### Frontend

- Vue 3
- TypeScript
- Vite
- HTML
- CSS

### AI Integration

- Google Gemini API
- Gemini Embedding API (`gemini-embedding-001`)
- Vector embeddings
- Retrieval-Augmented Generation (RAG)
- Cosine similarity search

### Testing and CI

- pytest
- HTTPX
- GitHub Actions

## Deployment & Infrastructure

| Component | Technology / Platform |
|---|---|
| Frontend Hosting | Render |
| Backend Hosting | Render |
| Database | PostgreSQL on Neon |
| Vector Search | pgvector |
| Database Migrations | Alembic |
| CI | GitHub Actions |

The frontend and backend are deployed separately on Render. The backend connects to a cloud-hosted PostgreSQL database on Neon through environment variables configured in Render.

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

### 5. Configure PostgreSQL and pgvector

Make sure PostgreSQL is running and the database has been created.

Enable the pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6. Run database migrations

From the project root:

```bash
python -m alembic upgrade head
```

### 7. Run the backend

```bash
python -m uvicorn app.main:app --reload
```

Backend API:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

Interactive API documentation:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 8. Configure and run the frontend

Open a second terminal:

```powershell
cd frontend
npm install
```

Create a `.env` file in the frontend directory if you need to configure a custom backend URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Open the frontend at:

[http://localhost:5173](http://localhost:5173)

## Running Tests

Run the automated backend tests from the project root:

```bash
python -m pytest -v
```

AI integration tests use mocked responses, so automated tests do not require actual Gemini API requests.

GitHub Actions automatically runs the test suite when changes are pushed to the repository.

The RAG pipeline has also been manually tested with saved job descriptions, including semantic retrieval, answer generation, and source retrieval.

## Future Improvements

- Resume upload and parsing.
- AI-powered resume and job description matching.
- Personalized interview feedback.
- Interview history and progress tracking.
- Improved retrieval and ranking for longer job descriptions.

## Author

Developed as a full-stack software engineering project using Python, FastAPI, Vue.js, PostgreSQL, pgvector, and Google Gemini.