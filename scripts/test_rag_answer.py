import traceback

from app.database import Sessionlocal
from app.services.rag.retrieval_service import search_relevant_chunks
from app.services.rag.answer_service import generate_rag_answer


def main():
    db = Sessionlocal()

    try:
        question = "What programming languages are required for this position?"

        # Step 1: Retrieve relevant information
        chunks = search_relevant_chunks(
            db=db,
            job_application_id=6,
            query=question,
            top_k=3
        )

        print("\nRetrieved chunks:")
        for chunk in chunks:
            print(chunk)

        # Step 2: Generate an answer using Gemini
        answer = generate_rag_answer(
            question=question,
            retrieved_chunks=chunks
        )

        print("\nAI Answer:")
        print(answer)

    except Exception:
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()