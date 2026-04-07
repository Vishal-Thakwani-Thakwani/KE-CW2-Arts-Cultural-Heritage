import json
import os
import re

RAW_DIR = "data/unstructured/raw"
OUTPUT_FILE = "data/unstructured/cleaned/cleaned_pages.jsonl"

def clean_text(text):
    """Remove Wikipedia noise and normalise text."""
    # Remove citation markers e.g. [1], [23]
    text = re.sub(r"\[\d+\]", "", text)
    # Remove edit section markers e.g. [edit]
    text = re.sub(r"\[edit\]", "", text)
    # Remove image captions e.g. thumb|, left|, right|
    text = re.sub(r"\b(thumb|left|right|center|upright|frame)\|", "", text)
    # Remove anything inside curly braces e.g. {{cite web}}
    text = re.sub(r"\{\{.*?\}\}", "", text)
    # Remove URLs
    text = re.sub(r"http\S+", "", text)
    # Remove lines that are just whitespace or single characters
    lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 1]
    text = " ".join(lines)
    # Collapse multiple spaces
    text = re.sub(r" +", " ", text)
    return text.strip()

def split_into_sections(text):
    """
    Split text into named sections based on common Wikipedia headings.
    Falls back to a single 'main' section if no headings are found.
    """
   
    section_keywords = [
        "early life", "biography", "life", "career", "style",
        "legacy", "works", "exhibitions", "awards", "death",
        "history", "collection", "location", "architecture"
    ]

    sections = []
    current_section = "main"
    current_text = []

    for sentence in text.split(". "):
        sentence_lower = sentence.lower().strip()
        matched = False
        for keyword in section_keywords:
            if sentence_lower.startswith(keyword) and len(sentence.strip()) < 60:
                
                if current_text:
                    sections.append({
                        "section": current_section,
                        "text": ". ".join(current_text).strip()
                    })
                current_section = keyword
                current_text = []
                matched = True
                break
        if not matched:
            current_text.append(sentence)

   
    if current_text:
        sections.append({
            "section": current_section,
            "text": ". ".join(current_text).strip()
        })

    return sections if sections else [{"section": "main", "text": text}]

def process_file(filepath):
    """Load a raw JSON file, clean and section the text."""
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    cleaned = clean_text(data["raw_text"])
    sections = split_into_sections(cleaned)

    return {
        "doc_id": data["id"],
        "title": data["title"],
        "entity_type": data["entity_type"],
        "url": data["url"],
        "sections": sections
    }

def main():
    print("=== Cleaning raw Wikipedia text ===")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    count = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for root, _, files in os.walk(RAW_DIR):
            for file in files:
                if file.endswith(".json"):
                    filepath = os.path.join(root, file)
                    print(f"  Cleaning: {file}")
                    result = process_file(filepath)
                    out.write(json.dumps(result, ensure_ascii=False) + "\n")
                    count += 1

    print(f"=== Done — {count} files cleaned → {OUTPUT_FILE} ===")

if __name__ == "__main__":
    main()