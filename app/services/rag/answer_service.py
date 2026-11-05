from google.genai import types

from app.core.ai_service import get_gemini_client


GENERATIVE_MODEL = "gemini-3.5-flash-lite"


def generate_rag_answer(
    question: str,
    retrieved_chunks: list[str]
) -> str:

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not retrieved_chunks:
        return "I couldn't find relevant information in this job description."

    # Combine retrieved chunks into one context
    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
You are an AI job assistant.

Answer the user's question using ONLY the information
provided in the job description context below.

If the answer is not available in the context,
clearly say that the job description does not specify it.

Do not invent requirements or responsibilities.

Job Description Context:
{context}

User Question:
{question}

Answer:
"""

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GENERATIVE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2
        )
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()