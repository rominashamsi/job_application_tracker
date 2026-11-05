
from sqlalchemy.orm import Session

from app.models import JobApplicationChunk
from .embedding_service import generate_document_embeddings


def split_text_into_chunks(
    text: str,
    chunk_size_words: int = 200,
    overlap_words: int = 40
) -> list[str]:

    if not text or not text.strip():
        return []

    if chunk_size_words <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap_words < 0 or overlap_words >= chunk_size_words:
        raise ValueError("Invalid overlap size.")

    words = text.split()
    chunks = []

    step = chunk_size_words - overlap_words

    for start in range(0, len(words), step):

        chunk_words = words[start:start + chunk_size_words]

        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))

        if start + chunk_size_words >= len(words):
            break

    return chunks


def replace_job_application_chunks(
    db: Session,
    job_application_id: int,
    text: str
) -> int:
    """
    Split a job description, generate embeddings,
    and replace its existing chunks.
    """

    chunks = split_text_into_chunks(text)

    # Generate all embeddings before deleting old chunks.
    embeddings = generate_document_embeddings(chunks)

    if len(chunks) != len(embeddings):
        raise RuntimeError("Chunks and embeddings count mismatch.")

    # Delete previously stored chunks.
    db.query(JobApplicationChunk).filter(
        JobApplicationChunk.job_application_id == job_application_id
    ).delete(synchronize_session=False)

    # Create new database records.
    records = [
        JobApplicationChunk(
            job_application_id=job_application_id,
            chunk_index=index,
            content=chunk,
            embedding=embedding
        )
        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        )
    ]

    db.add_all(records)

    # Send changes to the current transaction, without committing it.
    db.flush()

    return len(records)
