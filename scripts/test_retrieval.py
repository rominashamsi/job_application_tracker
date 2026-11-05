from app.database import Sessionlocal
from app.services.rag.retrieval_service import search_relevant_chunks


def main():
    db = Sessionlocal()

    try:
        results = search_relevant_chunks(
            db=db,
            job_application_id=6,
            query="What skills are required for this Junior AI Engineer position?",
            top_k=3
        )

        print("\nRetrieved chunks:")

        for index, chunk in enumerate(results, start=1):
            print(f"\nChunk {index}:")
            print(chunk)

        if not results:
            print("No relevant chunks found.")

    except Exception as error:
        print("Error:", error)

    finally:
        db.close()


if __name__ == "__main__":
    main()