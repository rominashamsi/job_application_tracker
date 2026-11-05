from sqlalchemy.orm import Session

from app.models import JobApplicationChunk
from app.services.rag.embedding_service import generate_query_embedding


def search_relevant_chunks(
    db: Session,
    job_application_id: int,
    query: str,
    top_k: int = 5
) -> list[str]:

    if not query or not query.strip():
        return []

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    # Convert the user's question into an embedding
    query_embedding = generate_query_embedding(query)

    # Find the most relevant chunks using cosine distance
    matching_chunks = (
        db.query(JobApplicationChunk)
        .filter(
            JobApplicationChunk.job_application_id == job_application_id
        )
        .order_by(
            JobApplicationChunk.embedding.cosine_distance(query_embedding)
        )
        .limit(top_k)
        .all()
    )

    # Return only the text of the retrieved chunks
    return [chunk.content for chunk in matching_chunks]