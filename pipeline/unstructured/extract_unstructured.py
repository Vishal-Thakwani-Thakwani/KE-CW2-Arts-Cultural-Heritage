import json
import os
import re
import spacy

INPUT_FILE = "pipeline/unstructured/data/chunked/chunks.jsonl"
OUTPUT_FILE = "pipeline/unstructured/data/extracted/extracted_facts.jsonl"

nlp = spacy.load("en_core_web_sm")

DATE_CONTEXT_RULES = {
    "artist": {
        "hasBirthDate": ["born", "birth", "baptised", "baptized"],
        "deathYear":    ["died", "death", "passed away", "deceased"]
    },
    "artwork": {
        "creationYear": ["painted", "created", "completed", "commissioned",
                         "produced", "made", "executed", "finished", "begun"]
    },
    "museum": {
        "foundedYear": ["founded", "opened", "established", "inaugurated",
                        "built", "created", "constructed"]
    }
}

ENTITY_TO_PREDICATE = {
    "PERSON": "createdBy",
    "GPE":    "locatedIn",
    "LOC":    "locatedIn",
    "ORG":    "heldBy",
    "NORP":   "nationality",
    "EVENT":  "exhibitedIn",
}

def refine_predicate(predicate, entity_type, entity_label):
    if entity_label == "PERSON":
        if entity_type == "artwork":
            return "createdBy"
        elif entity_type == "artist":
            return "influencedBy"
    if entity_label in ("GPE", "LOC"):
        if entity_type == "artist":
            return "bornIn"
        elif entity_type in ("museum", "artwork"):
            return "locatedIn"
    if entity_label == "ORG":
        if entity_type in ("artwork", "artist"):
            return "heldBy"
    if entity_label == "NORP":
        if entity_type == "artist":
            return "nationality"
    return predicate

def extract_date_triple(ent, chunk):
    entity_type = chunk["entity_type"]
    if entity_type not in DATE_CONTEXT_RULES:
        return None
    sent_lower = ent.sent.text.lower()
    rules = DATE_CONTEXT_RULES[entity_type]
    for predicate, keywords in rules.items():
        for keyword in keywords:
            if keyword in sent_lower:
                year_match = re.search(r"\b(\d{4})\b", ent.text)
                if year_match:
                    year = int(year_match.group(1))
                    if entity_type == "artist" and not (1200 <= year <= 2000):
                        continue
                    if entity_type == "artwork" and not (1200 <= year <= 2024):
                        continue
                    if entity_type == "museum" and not (1600 <= year <= 2024):
                        continue
                    return {
                        "subject": chunk["title"],
                        "predicate": predicate,
                        "object": year_match.group(1),
                        "confidence": 0.85,
                        "evidence": ent.sent.text.strip(),
                        "ner_label": "DATE"
                    }
    return None

def extract_triples(chunk):
    doc = nlp(chunk["text"])
    triples = []
    seen = set()

    for ent in doc.ents:
        if ent.label_ == "DATE":
            triple = extract_date_triple(ent, chunk)
            if triple:
                key = (triple["subject"], triple["predicate"], triple["object"])
                if key not in seen:
                    seen.add(key)
                    triples.append(triple)
            continue

        if ent.label_ not in ENTITY_TO_PREDICATE:
            continue

        base_predicate = ENTITY_TO_PREDICATE[ent.label_]
        predicate = refine_predicate(base_predicate, chunk["entity_type"], ent.label_)
        subject = chunk["title"]
        obj = ent.text.strip()

        if obj.lower() == subject.lower():
            continue
        if len(obj) < 3:
            continue
        if obj.lower().startswith("the "):
            continue
        if obj.lower().endswith("'s") or obj.lower().endswith("s'"):
            continue

        triple_key = (subject, predicate, obj)
        if triple_key in seen:
            continue
        seen.add(triple_key)

        triples.append({
            "subject": subject,
            "predicate": predicate,
            "object": obj,
            "confidence": 0.75,
            "evidence": ent.sent.text.strip(),
            "ner_label": ent.label_
        })

    return triples

def main():
    print("=== Extracting triples using spaCy NER ===")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    total_triples = 0
    total_chunks = 0
    skipped = 0
    seen_date_predicates = {}

    with open(INPUT_FILE, encoding="utf-8") as f, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as out:

        for line in f:
            chunk = json.loads(line)
            total_chunks += 1

            if not chunk["text"].strip():
                skipped += 1
                continue

            triples = extract_triples(chunk)

            for triple in triples:
                if triple["ner_label"] == "DATE":
                    date_key = (triple["subject"], triple["predicate"])
                    if date_key in seen_date_predicates:
                        continue
                    seen_date_predicates[date_key] = triple["object"]

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

if __name__ == "__m