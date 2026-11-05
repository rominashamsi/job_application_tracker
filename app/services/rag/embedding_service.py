
from google.genai import types

from app.core.ai_service import get_gemini_client


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768


def _generate_embeddings(
    texts: list[str],
    task_type: str
) -> list[list[float]]:

    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError("Texts cannot be empty.")

    client = get_gemini_client()

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSIONS
        )
    )

    embeddings = response.embeddings

    if embeddings is None or len(embeddings) != len(texts):
        raise RuntimeError("Invalid number of embeddings returned.")

    vectors = []

    for item in embeddings:
        values = item.values

        if values is None or len(values) != EMBEDDING_DIMENSIONS:
            raise RuntimeError("Invalid embedding dimensions.")

        vectors.append(values)

    return vectors


def generate_document_embeddings(
    texts: list[str]
) -> list[list[float]]:
    """Generate embeddings for multiple document chunks."""

    return _generate_embeddings(
        texts,
        task_type="RETRIEVAL_DOCUMENT"
    )


def generate_document_embedding(text: str) -> list[float]:
    """Generate embedding for one document."""

    return generate_document_embeddings([text])[0]


def generate_query_embedding(text: str) -> list[float]:
    """Generate embedding for a user's question."""

    return _generate_embeddings(
        [text],
        task_type="RETRIEVAL_QUERY"
    )[0]
