from pathlib import Path

from engine.policy_retriever import ingest_policy_source


BASE_DIR = Path(__file__).resolve().parent.parent
RBI_DIR = BASE_DIR / "knowledge_base" / "rbi"


RBI_POLICY_SOURCES = [
    {
        "file_name": "rbi_key_facts_statement.txt",
        "source_type": "RBI_REGULATORY_GUIDANCE",
        "source_title": (
            "RBI Key Facts Statement (KFS) "
            "for Loans and Advances"
        ),
        "source_url": (
            "https://www.rbi.org.in/Scripts/"
            "NotificationUser.aspx?Id=12663&Mode=0"
        ),
    },
    {
        "file_name": "rbi_fair_practices_code.txt",
        "source_type": "RBI_REGULATORY_GUIDANCE",
        "source_title": (
            "RBI Fair Practices Code for Lenders"
        ),
        "source_url": (
            "https://www.rbi.org.in/Scripts/"
            "NotificationUser.aspx?Id=1172&Mode=0"
        ),
    },
]


def load_rbi_policy_file(file_name):
    """
    Load an RBI regulatory-guidance knowledge file.
    """

    file_path = RBI_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"RBI knowledge file was not found: {file_path}"
        )

    return file_path.read_text(
        encoding="utf-8"
    ).strip()


def split_rbi_policy_into_chunks(policy_text):
    """
    Split an RBI knowledge file into numbered sections.

    Introductory metadata is retained as the first chunk,
    followed by the numbered regulatory-guidance sections.
    """

    lines = policy_text.splitlines()

    chunks = []
    current_chunk = []

    for line in lines:
        stripped_line = line.strip()

        is_numbered_heading = (
            len(stripped_line) >= 3
            and stripped_line[0].isdigit()
            and ". " in stripped_line
        )

        if (
            is_numbered_heading
            and current_chunk
        ):
            chunk_text = "\n".join(
                current_chunk
            ).strip()

            if chunk_text:
                chunks.append(
                    chunk_text
                )

            current_chunk = []

        current_chunk.append(line)

    if current_chunk:
        chunk_text = "\n".join(
            current_chunk
        ).strip()

        if chunk_text:
            chunks.append(
                chunk_text
            )

    return chunks


def ingest_rbi_policy(source):
    """
    Load, chunk, embed, and store one RBI policy source.
    """

    policy_text = load_rbi_policy_file(
        source["file_name"]
    )

    chunks = split_rbi_policy_into_chunks(
        policy_text
    )

    if not chunks:
        raise ValueError(
            "No chunks were generated for "
            f"{source['file_name']}."
        )

    print()
    print(
        f"Ingesting: {source['source_title']}"
    )

    print(
        f"Generated chunks: {len(chunks)}"
    )

    stored_count = ingest_policy_source(
        source_name=source["file_name"],
        source_type=source["source_type"],
        source_title=source["source_title"],
        source_url=source["source_url"],
        chunks=chunks,
    )

    return stored_count


def main():
    """
    Ingest every configured RBI regulatory-guidance
    source into PostgreSQL + pgvector.
    """

    print(
        "Starting RBI regulatory-guidance ingestion..."
    )

    total_chunks = 0

    for source in RBI_POLICY_SOURCES:
        stored_count = ingest_rbi_policy(
            source
        )

        total_chunks += stored_count

    print()
    print(
        "RBI ingestion completed successfully."
    )

    print(
        f"RBI sources processed: "
        f"{len(RBI_POLICY_SOURCES)}"
    )

    print(
        f"Total RBI chunks stored: "
        f"{total_chunks}"
    )


if __name__ == "__main__":
    main()