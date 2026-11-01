from app.core.ai_service import generate_interview_questions


def main():
    questions = generate_interview_questions(
        "Junior Python Developer"
    )
    print(questions)


if __name__ == "__main__":
    main()