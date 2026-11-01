import pytest

from app.routes import ai as ai_routes


# Helper: Register a user and log in
def register_and_login(client):
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "ai.test@example.com",
            "password": "TestPass123",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ai.test@example.com",
            "password": "TestPass123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


# Test 1: AI endpoints require authentication
@pytest.mark.parametrize(
    "endpoint",
    [
        "/ai/interview-questions",
        "/ai/interview-questions/stream",
    ],
)
def test_ai_requires_token(client, endpoint):
    response = client.post(
        endpoint,
        json={"job_title": "Junior Backend Developer"},
    )

    assert response.status_code == 401


# Test 2: Generate interview questions successfully
def test_generate_interview_questions(client, monkeypatch):
    headers = register_and_login(client)

    def fake_generate(job_title, previous_questions=None):
        return "1. What is Python?\n2. What is FastAPI?"

    monkeypatch.setattr(
        ai_routes,
        "generate_interview_questions",
        fake_generate,
    )

    response = client.post(
        "/ai/interview-questions",
        headers=headers,
        json={
            "job_title": "Junior Backend Developer",
            "previous_questions": None,
        },
    )

    assert response.status_code == 200
    assert response.json()["job_title"] == "Junior Backend Developer"
    assert "What is Python?" in response.json()["questions"]


# Test 3: Previous questions are passed to the AI service
def test_generate_questions_uses_previous_questions(client, monkeypatch):
    headers = register_and_login(client)

    received_data = {}

    def fake_generate(job_title, previous_questions=None):
        received_data["job_title"] = job_title
        received_data["previous_questions"] = previous_questions

        return "1. What is SQLAlchemy?"

    monkeypatch.setattr(
        ai_routes,
        "generate_interview_questions",
        fake_generate,
    )

    previous_questions = "1. What is Python?"

    response = client.post(
        "/ai/interview-questions",
        headers=headers,
        json={
            "job_title": "Junior Backend Developer",
            "previous_questions": previous_questions,
        },
    )

    assert response.status_code == 200
    assert received_data["job_title"] == "Junior Backend Developer"
    assert received_data["previous_questions"] == previous_questions


# Test 4: Stream interview questions successfully
def test_stream_interview_questions(client, monkeypatch):
    headers = register_and_login(client)

    received_data = {}

    def fake_stream(job_title, previous_questions=None):
        received_data["job_title"] = job_title
        received_data["previous_questions"] = previous_questions

        yield "1. What is Python?\n"
        yield "2. What is FastAPI?"

    monkeypatch.setattr(
        ai_routes,
        "stream_interview_questions",
        fake_stream,
    )

    previous_questions = "1. What is SQL?"

    response = client.post(
        "/ai/interview-questions/stream",
        headers=headers,
        json={
            "job_title": "Junior Backend Developer",
            "previous_questions": previous_questions,
        },
    )

    assert response.status_code == 200
    assert "What is Python?" in response.text
    assert "What is FastAPI?" in response.text

    assert received_data["job_title"] == "Junior Backend Developer"
    assert received_data["previous_questions"] == previous_questions