from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_FILE = BASE_DIR / "knowledge_base" / "lending_policy.txt"


def load_policy():
    with open(POLICY_FILE, "r", encoding="utf-8") as file:
        policy_text = file.read()

    return policy_text


def split_policy_into_chunks(policy_text):
    pattern = r"(?=\n\d+\.\s+[A-Z])"

    sections = re.split(pattern, policy_text)

    chunks = []

    for section in sections:
        cleaned_section = section.strip()

        if cleaned_section:
            chunks.append(cleaned_section)

    return chunks


if __name__ == "__main__":
    policy = load_policy()

    chunks = split_policy_into_chunks(policy)

    print("Total chunks:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n--- CHUNK {index} ---")
        print(chunk)