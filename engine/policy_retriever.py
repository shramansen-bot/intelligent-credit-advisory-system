import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from engine.database import get_database_connection
from engine.policy_loader import (
    load_policy,
    split_policy_into_chunks,
)


load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768


# =========================================================
# POLICY SOURCE DEFINITIONS
# =========================================================

INTERNAL_POLICY_SOURCE = {
    "source_name": "lending_policy.txt",
    "source_type": "INTERNAL_POLICY",
    "source_title": "Synthetic Lending Policy",
    "source_url": None,
}


# =========================================================
# GEMINI CLIENT
# =========================================================

def get_gemini_client():
    """
    Create the Gemini client only when actually required.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found. "
            "Create a .env file using .env.example "
            "and add your API key."
        )

    return genai.Client(api_key=api_key)


# =========================================================
# EMBEDDING GENERATION
# =========================================================

def create_embedding(text, task_type):
    """
    Generate a 768-dimensional Gemini embedding.
    """
    client = get_gemini_client()

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )

    return response.embeddings[0].values


# =========================================================
# PGVECTOR SERIALIZATION
# =========================================================

def embedding_to_pgvector(embedding):
    """
    Convert a Python list into the textual vector format
    accepted by PostgreSQL pgvector.
    """
    return "[" + ",".join(
        str(value)
        for value in embedding
    ) + "]"


# =========================================================
# DATABASE INSERTION
# =========================================================

def store_policy_chunks(
    source_name,
    source_type,
    source_title,
    source_url,
    chunks,
):
    """
    Generate embeddings for policy chunks and store them
    in PostgreSQL with source metadata.

    Existing chunks belonging to the same source are replaced.
    """
    if not chunks:
        raise ValueError(
            f"No policy chunks were supplied for {source_name}."
        )

    print(
        f"Generating embeddings for {len(chunks)} chunks "
        f"from {source_title}..."
    )

    embedded_chunks = []

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):
        print(
            f"Embedding chunk {index}/{len(chunks)} "
            f"from {source_name}..."
        )

        embedding = create_embedding(
            chunk,
            task_type="RETRIEVAL_DOCUMENT",
        )

        embedded_chunks.append(
            (
                source_name,
                source_type,
                source_title,
                source_url,
                chunk,
                embedding_to_pgvector(
                    embedding
                ),
            )
        )

    delete_query = """
        DELETE FROM policy_chunks
        WHERE source_name = %s;
    """

    insert_query = """
        INSERT INTO policy_chunks (
            source_name,
            source_type,
            source_title,
            source_url,
            chunk_text,
            embedding
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s::vector
        );
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                delete_query,
                (source_name,),
            )

            for item in embedded_chunks:
                cursor.execute(
                    insert_query,
                    item,
                )

        connection.commit()

    print(
        f"Stored {len(embedded_chunks)} chunks "
        f"for {source_title}."
    )

    return len(embedded_chunks)


# =========================================================
# INTERNAL POLICY INDEX
# =========================================================

def build_internal_policy_index():
    """
    Load the synthetic internal lending policy, split it
    into sections, and store its embeddings in pgvector.
    """
    policy_text = load_policy()

    chunks = split_policy_into_chunks(
        policy_text
    )

    return store_policy_chunks(
        source_name=(
            INTERNAL_POLICY_SOURCE["source_name"]
        ),
        source_type=(
            INTERNAL_POLICY_SOURCE["source_type"]
        ),
        source_title=(
            INTERNAL_POLICY_SOURCE["source_title"]
        ),
        source_url=(
            INTERNAL_POLICY_SOURCE["source_url"]
        ),
        chunks=chunks,
    )


# =========================================================
# INDEX STATUS
# =========================================================

def policy_source_exists(source_name):
    """
    Check whether PostgreSQL already contains chunks
    belonging to a particular source.
    """
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM policy_chunks
            WHERE source_name = %s
        );
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (source_name,),
            )

            return cursor.fetchone()[0]


def ensure_internal_policy_index():
    """
    Ensure the synthetic internal policy is available
    in PostgreSQL.
    """
    source_name = (
        INTERNAL_POLICY_SOURCE["source_name"]
    )

    if not policy_source_exists(
        source_name
    ):
        print(
            "Internal policy embeddings were not "
            "found in PostgreSQL."
        )

        build_internal_policy_index()


# =========================================================
# GENERAL MULTI-SOURCE INGESTION
# =========================================================

def ingest_policy_source(
    source_name,
    source_type,
    source_title,
    source_url,
    chunks,
):
    """
    Public ingestion function for adding additional policy
    or regulatory sources to the pgvector knowledge base.

    This will later be used for RBI regulatory guidance.
    """
    return store_policy_chunks(
        source_name=source_name,
        source_type=source_type,
        source_title=source_title,
        source_url=source_url,
        chunks=chunks,
    )


# =========================================================
# SEMANTIC RETRIEVAL
# =========================================================

def retrieve_relevant_policy(
    query,
    top_k=2,
    source_type=None,
):
    """
    Retrieve semantically relevant policy chunks using
    PostgreSQL + pgvector cosine-distance search.

    When source_type is provided, retrieval can be restricted
    to a particular source category such as:

        INTERNAL_POLICY
        RBI_REGULATORY_GUIDANCE

    When source_type is None, all policy sources are searched.
    """
    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    ensure_internal_policy_index()

    query_embedding = create_embedding(
        query,
        task_type="RETRIEVAL_QUERY",
    )

    query_vector = embedding_to_pgvector(
        query_embedding
    )

    if source_type is None:
        search_query = """
            SELECT
                chunk_id,
                source_name,
                source_type,
                source_title,
                source_url,
                chunk_text,
                1 - (
                    embedding <=> %s::vector
                ) AS similarity
            FROM policy_chunks
            ORDER BY
                embedding <=> %s::vector
            LIMIT %s;
        """

        parameters = (
            query_vector,
            query_vector,
            top_k,
        )

    else:
        search_query = """
            SELECT
                chunk_id,
                source_name,
                source_type,
                source_title,
                source_url,
                chunk_text,
                1 - (
                    embedding <=> %s::vector
                ) AS similarity
            FROM policy_chunks
            WHERE source_type = %s
            ORDER BY
                embedding <=> %s::vector
            LIMIT %s;
        """

        parameters = (
            query_vector,
            source_type,
            query_vector,
            top_k,
        )

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                search_query,
                parameters,
            )

            rows = cursor.fetchall()

    results = []

    for row in rows:
        results.append(
            {
                "chunk_id": row[0],
                "source_name": row[1],
                "source_type": row[2],
                "source_title": row[3],
                "source_url": row[4],
                "text": row[5],
                "similarity": float(row[6]),
            }
        )

    return results


# =========================================================
# MANUAL TEST
# =========================================================

if __name__ == "__main__":
    test_query = (
        "Why would a customer fail "
        "the affordability check?"
    )

    results = retrieve_relevant_policy(
        test_query,
        top_k=3,
    )

    print("\nQuery:")
    print(test_query)

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"\n--- RESULT {index} ---"
        )

        print(
            "Source type:",
            result["source_type"],
        )

        print(
            "Source:",
            result["source_title"],
        )

        if result["source_url"]:
            print(
                "URL:",
                result["source_url"],
            )

        print(
            "Similarity:",
            round(
                result["similarity"],
                4,
            ),
        )

        print(result["text"])