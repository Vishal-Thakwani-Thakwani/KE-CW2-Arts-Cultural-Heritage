import json
import os
import spacy

INPUT_FILE = "data/unstructured/chunked/chunks.jsonl"
OUTPUT_FILE = "data/unstructured/extracted/extracted_facts.jsonl"

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Map spaCy entity labels to our ontology properties
# Based on the domain concept sketch properties
ENTITY_TO_PREDICATE = {
    "PERSON": "createdBy",       # people mentioned = likely creators
    "GPE": "locatedIn",          # countries, cities = locations
    "LOC": "locatedIn",          # geographic locations
    "ORG": "heldBy",             # organisations = likely institutions
    "DATE": "creationYear",      # dates = creation or birth years
    "NORP": "nationality",       # nationalities, movements
    "WORK_OF_ART": "hasGenre",   # artwork titles mentioned
    "EVENT": "exhibitedIn",      # events = likely exhibitions
}

def refine_predicate(predicate, entity_type, entity_label):
    """
    Refine the predicate based on context.
    e.g. a PERSON in an artwork document is more likely createdBy
    a GPE in an artist document is more likely bornIn
    """
    if entity_label == "PERSON":
        if entity_type == "artwork":
            return "createdBy"
        elif entity_type == "artist":
            return "influencedBy"

    if entity_label in ("GPE", "LOC"):
        if entity_type == "artist":
            return "bornIn"
        elif entity_type == "museum":
            return "locatedIn"
        elif entity_type == "artwork":
            return "locatedIn"

    if entity_label == "ORG":
        if entity_type in ("artwork", "artist"):
            return "heldBy"

    if entity_label == "DATE":
        if entity_type == "artist":
            return "birthYear"
        elif entity_type == "artwork":
            return "creationYear"
        elif entity_type == "museum":
            return "foundedYear"

    if entity_label == "NORP":
        if entity_type == "artist":
            return "nationality"

    return predicate

def extract_triples(chunk):
    """
    Use spaCy NER to extract triples from a text chunk.
    Returns a list of triple dicts.
    """
    doc = nlp(chunk["text"])
    triples = []
    seen = set()  # avoid duplicate triples

    for ent in doc.ents:
        if ent.label_ not in ENTITY_TO_PREDICATE:
            continue

        base_predicate = ENTITY_TO_PREDICATE[ent.label_]
        predicate = refine_predicate(
            base_predicate,
            chunk["entity_type"],
            ent.label_
        )

        subject = chunk["title"]
        obj = ent.text.strip()

        # Skip if object is same as subject or too short
        if obj.lower() == subject.lower() or len(obj) < 2:
            continue

        # Skip duplicate triples
        triple_key = (subject, predicate, obj)
        if triple_key in seen:
            continue
        seen.add(triple_key)

        # Find the sentence containing this entity as evidence
        sent = ent.sent.text.strip()

        triples.append({
            "subject": subject,
            "predicate": predicate,
            "object": obj,
            "confidence": 0.75,  
            "evidence": sent,
            "ner_label": ent.label_  
        })

    return triples

def main():
    print("=== Extracting triples using spaCy NER ===")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    total_triples = 0
    total_chunks = 0
    skipped = 0

    with open(INPUT_FILE, encoding="utf-8") as f, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        for line in f:
            chunk = json.loads(line)
            total_chunks += 1

            if not chunk["text"].strip():
                skipped += 1
                continue

            print(f"  Processing chunk {chunk['chunk_id']} "
                  f"({chunk['entity_type']}: {chunk['title']})...")

            triples = extract_triples(chunk)

            for triple in triples:
                record = {
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "title": chunk["title"],
                    "entity_type": chunk["entity_type"],
                    "section": chunk["section"],
                    "label": chunk["label"],
                    "subject": triple["subject"],
                    "predicate": triple["predicate"],
                    "object": triple["object"],
                    "confidence": triple["confidence"],
                    "evidence": triple["evidence"],
                    "ner_label": triple["ner_label"]
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_triples += 1

    print(f"=== Done ===")
    print(f"    Chunks processed : {total_chunks}")
    print(f"    Chunks skipped   : {skipped}")
    print(f"    Triples extracted: {total_triples}")
    print(f"    Output           : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()