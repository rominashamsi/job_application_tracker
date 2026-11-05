
import os
import math
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Two sample job-related sentences
texts = [
    "Python developer with FastAPI experience",
    "Backend engineer skilled in Python"
]

# Generate embeddings for both texts
response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=texts,
    config=types.EmbedContentConfig(
        task_type="SEMANTIC_SIMILARITY",
        output_dimensionality=768
    )
)

vector1 = response.embeddings[0].values
vector2 = response.embeddings[1].values


def cosine_similarity(vector1, vector2):
    dot_product = sum(a * b for a, b in zip(vector1, vector2))

    norm1 = math.sqrt(sum(a * a for a in vector1))
    norm2 = math.sqrt(sum(b * b for b in vector2))

    if norm1 == 0 or norm2 == 0:
        raise ValueError("A vector cannot have zero length.")

    return dot_product / (norm1 * norm2)


score = cosine_similarity(vector1, vector2)

print("Similarity score:", round(score, 4))
