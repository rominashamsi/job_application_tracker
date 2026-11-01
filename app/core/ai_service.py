
import os
import time
from collections.abc import Iterator

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load environment variables from .env
def get_gemini_client():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=60_000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


# Build the prompt for interview question generation
def _build_interview_prompt(
    job_title: str,
    previous_questions: str | None = None,
) -> str:

    previous_section = (
        previous_questions.strip()
        if previous_questions and previous_questions.strip()
        else "No previous questions."
    )

    prompt = f"""
You are an interview preparation assistant.

Generate exactly 5 interview questions for this job position:
{job_title}

Question requirements:
- Generate exactly 3 technical questions.
- Generate exactly 2 behavioral questions.
- Make all questions relevant to the job position.
- Keep questions clear and concise.
- Number the questions from 1 to 5.
- Clearly label each question as Technical or Behavioral.
- Return only the questions. Do not add an introduction or conclusion.

Previously generated questions:
{previous_section}

Important:
- Do not repeat any previous question.
- Do not create slightly reworded versions of previous questions.
- Explore different skills, concepts, and scenarios.
- Focus on new topics that have not been covered before.
"""

    return prompt.strip()


# Generate all interview questions at once
def generate_interview_questions(
    job_title: str,
    previous_questions: str | None = None,
) -> str:
    client = get_gemini_client()
    prompt = _build_interview_prompt(
        job_title,
        previous_questions,
    )

    start_time = time.perf_counter()
    print("Sending request to Gemini...")

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level="low"
                )
            ),
        )

    except Exception as error:
        elapsed_time = time.perf_counter() - start_time

        print(
            f"Gemini request failed after "
            f"{elapsed_time:.2f} seconds."
        )
        print(f"Error type: {type(error).__name__}")
        print(f"Error details: {error}")

        raise

    elapsed_time = time.perf_counter() - start_time

    print(
        f"Gemini response received in "
        f"{elapsed_time:.2f} seconds."
    )

    return response.text or ""


# Stream interview questions gradually
def stream_interview_questions(
    job_title: str,
    previous_questions: str | None = None,
) -> Iterator[str]:
    client = get_gemini_client()
    prompt = _build_interview_prompt(
        job_title,
        previous_questions,
    )

    start_time = time.perf_counter()
    print("Starting Gemini streaming request...")

    try:
        for chunk in client.models.generate_content_stream(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level="low"
                )
            ),
        ):
            if chunk.text:
                yield chunk.text

        elapsed_time = time.perf_counter() - start_time

        print(
            f"Gemini streaming completed in "
            f"{elapsed_time:.2f} seconds."
        )

    except Exception as error:
        elapsed_time = time.perf_counter() - start_time

        print(
            f"Gemini streaming failed after "
            f"{elapsed_time:.2f} seconds."
        )
        print(f"Error type: {type(error).__name__}")
        print(f"Error details: {error}")

        raise
