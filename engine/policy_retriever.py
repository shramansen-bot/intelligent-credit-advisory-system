import os
import math
import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from engine.policy_loader import load_policy, split_policy_into_chunks


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
VECTOR_STORE_FILE = VECTOR_STORE_DIR / "policy_embeddings.json"

_policy_index = None


def get_gemini_client():
    """
    Create the Gemini client only when it is actually needed.

    This allows the project modules and automated tests to be imported
    even when a GEMINI_API_KEY has not been configured.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found. "
            "Create a .env file using .env.example and add your API key."
        )

    return genai.Client(api_key=api_key)


def create_embedding(text, task_type):
    """
    Generate a Gemini embedding for the supplied text.
    """
    client = get_gemini_client()

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=768
        )
    )

    return response.embeddings[0].values


def cosine_similarity(vector_a, vector_b):
    """
    Calculate cosine similarity between two embedding vectors.
    """
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (magnitude_a * magnitude_b)


def build_policy_index():
    """
    Load the synthetic lending policy, split it into sections,
    and generate an embedding for every section.
    """
    policy = load_policy()
    chunks = split_policy_into_chunks(policy)

    policy_index = []

    print("Generating policy embeddings...")

    for chunk in chunks:
        embedding = create_embedding(
            chunk,
            task_type="RETRIEVAL_DOCUMENT"
        )

        policy_index.append(
            {
                "text": chunk,
                "embedding": embedding
            }
        )

    return policy_index


def save_policy_index(policy_index):
    """
    Save generated policy embeddings locally so that they do not
    need to be regenerated every time the application starts.
    """
    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        VECTOR_STORE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(policy_index, file)

    print("Policy embedding index saved to disk.")


def load_saved_policy_index():
    """
    Load the locally cached policy embedding index.
    """
    with open(
        VECTOR_STORE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        policy_index = json.load(file)

    print("Policy embedding index loaded from disk.")

    return policy_index


def get_policy_index():
    """
    Return the policy embedding index.

    The index is loaded from memory when available, otherwise from
    the local cache. If no cache exists, a new index is generated.
    """
    global _policy_index

    if _policy_index is not None:
        return _policy_index

    if VECTOR_STORE_FILE.exists():
        _policy_index = load_saved_policy_index()
    else:
        _policy_index = build_policy_index()
        save_policy_index(_policy_index)

    return _policy_index


def retrieve_relevant_policy(query, top_k=2):
    """
    Retrieve the policy sections that are semantically most relevant
    to the supplied query.
    """
    policy_index = get_policy_index()

    query_embedding = create_embedding(
        query,
        task_type="RETRIEVAL_QUERY"
    )

    scored_chunks = []

    for item in policy_index:
        similarity = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        scored_chunks.append(
            {
                "text": item["text"],
                "similarity": similarity
            }
        )

    scored_chunks.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return scored_chunks[:top_k]


if __name__ == "__main__":
    query = "Why would a customer fail the affordability check?"

    results = retrieve_relevant_policy(
        query,
        top_k=2
    )

    print("\nQuery:")
    print(query)

    for index, result in enumerate(results, start=1):
        print(f"\n--- RESULT {index} ---")
        print(
            "Similarity:",
            round(result["similarity"], 4)
        )
        print(result["text"])