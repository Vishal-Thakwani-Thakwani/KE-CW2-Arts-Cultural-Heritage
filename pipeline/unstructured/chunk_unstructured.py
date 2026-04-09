import json
import os

INPUT_FILE = "pipeline/unstructured/data/cleaned/cleaned_pages.jsonl"
OUTPUT_FILE = "pipeline/unstructured/data/chunked/chunks.jsonl"

# Map section names to meaningful labels for the knowledge graph
SECTION_LABEL_MAP = {
    "early life": "biography",
    "biography": "biography",
    "life": "biography",
    "career": "career",
    "style": "artistic_style",
    "legacy": "legacy",
    "works": "works",
    "exhibitions": "exhibitions",
    "awards": "awards",
    "death": "biography",
    "history": "history",
    "collection": "collection",
    "location": "location",
    "architecture": "architecture",
    "main": "general"
}

def label_section(section_name):
    """Map a section name to a KG-meaningful label."""
    for key in SECTION_LABEL_MAP:
        if key in section_name.lower():
            return SECTION_LABEL_MAP[key]
    return "general"

def chunk_section(text, max_chars=500):
    """
    Split a section's text into chunks.
    Tries to split on sentence boundaries rather than mid-sentence.
    """
    sentences = text.split(". ")
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue
        if current_len + len(sentence) > max_chars and current_chunk:
            chunks.append(". ".join(current_chunk).strip())
            current_chunk = [sentence]
            current_len = len(sentence)
        else:
            current_chunk.append(sentence)
            current_len += len(sentence)

    if current_chunk:
        chunks.append(". ".join(current_chunk).strip())

    return chunks

def main():
    print("=== Chunking cleaned text ===")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    total_chunks = 0
    with open(INPUT_FILE, encoding="utf-8") as f, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        for line in f:
            doc = json.loads(line)
            chunk_id = 0

            for section in doc["sections"]:
                label = label_section(section["section"])
                chunks = chunk_section(section["text"])

                for chunk_text in chunks:
                    chunk = {
                        "chunk_id": f"{doc['doc_id']}_{chunk_id}",
                        "doc_id": doc["doc_id"],
                        "title": doc["title"],
                        "entity_type": doc["entity_type"],
                        "section": section["section"],
                        "label": label,
                        "text": chunk_text
                    }
                    out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                    chunk_id += 1
                    total_chunks += 1

    print(f"=== Done — {total_chunks} chunks written → {OUTPUT_FILE} ===")

if __name__ == "__m