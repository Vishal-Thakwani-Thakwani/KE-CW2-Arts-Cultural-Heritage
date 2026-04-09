import csv
import json
import os
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup

BASE_DIR = "pipeline/unstructured/data/raw"
SOURCES_CSV = "pipeline/unstructured/unstructured_sources.csv"

def fetch_wikipedia_text(url):
    """Fetch and extract clean paragraph text from a Wikipedia page."""
    try:
        headers = {"User-Agent": "KE-Coursework2-KG-Builder/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted elements before extracting text
        for tag in soup.find_all(["table", "sup", "span.mw-editsection"]):
            tag.decompose()

        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text() for p in paragraphs if p.get_text().strip()])
        return text

    except requests.exceptions.RequestException as e:
        print(f"  ERROR fetching {url}: {e}")
        return None

def save_raw(entry):
    """Save raw fetched text as a JSON file in the correct folder."""
    entity_folder = entry["entity_type"] + "s"  
    folder = os.path.join(BASE_DIR, entity_folder)
    os.makedirs(folder, exist_ok=True)

    filename = entry["title"].lower().replace(" ", "_") + ".json"
    filepath = os.path.join(folder, filename)

    # Skip if already fetched
    if os.path.exists(filepath):
        print(f"  SKIP (already exists): {entry['title']}")
        return

    print(f"  Fetching: {entry['title']} ...")
    raw_text = fetch_wikipedia_text(entry["url"])

    if raw_text is None:
        print(f"  FAILED: {entry['title']}")
        return

    data = {
        "id": entry["id"],
        "title": entry["title"],
        "entity_type": entry["entity_type"],
        "url": entry["url"],
        "retrieved_at": datetime.now().isoformat(),
        "raw_text": raw_text
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  SAVED: {filepath}")
    time.sleep(1)  

def main():
    print("=== Fetching unstructured data from Wikipedia ===")
    with open(SOURCES_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            save_raw(row)
    print("=== Done ===")

if __name__ == "__main__":
    main()