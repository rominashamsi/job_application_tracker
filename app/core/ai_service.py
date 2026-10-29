import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)


def generate_interview_questions(job_title: str) -> str:
    prompt = (
        f"Generate 5 interview questions for a {job_title} position. "
        "Include a mix of technical and behavioral questions."
    )

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    return response.text or ""     