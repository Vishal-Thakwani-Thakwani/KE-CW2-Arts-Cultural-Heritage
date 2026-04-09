import json
import os
import re
import unicodedata
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD

INPUT_FILE = "pipeline/unstructured/data/extracted/extracted_facts.jsonl"
OUTPUT_FILE = "pipeline/unstructured/data/unstructured_triples.ttl"
SEED_FILE = "pipeline/unstructured/data/seed_triples.ttl"

CAH = Namespace("http://example.org/culturalheritage#")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
EDM = Namespace("http://www.europeana.eu/schemas/edm/")

PREDICATE_MAP = {
    "createdBy":    CAH.createdBy,
    "heldBy":       CAH.heldBy,
    "locatedIn":    CAH.locatedIn,
    "bornIn":       CAH.locatedIn,
    "influencedBy": CAH.influencedBy,
    "hasGenre":     CAH.hasGenre,
    "exhibitedIn":  CAH.participatedInExhibition,
    "activeIn":     CAH.activeInMovement,
    "wonAward":     CAH.wonPrize,
    "usedMedium":   CAH.usesMedium,
}

DATATYPE_PREDICATE_MAP = {
    "birthYear":   CAH.hasBirthDate,
    "creationYear": CAH.hasCreationDate,
    "deathYear":   CAH.hasBirthDate,
    "foundedYear": CAH.hasCreationDate,
    "hasBirthDate": CAH.hasBirthDate,
}

CLASS_MAP = {
    "artist":  CAH.Artist,
    "artwork": CAH.Artwork,
    "museum":  CAH.Museum,
}

# Objects that look like entities but aren't useful
BLOCKLIST = {
    "1st earl", "2nd earl", "3rd earl",
    "2 place lamartine", "place lamartine",
    "école", "ecole",
    "émile bernard", "emile bernard",
    "4457 van gogh",
    "étienne la font de saint-yenne",
}

# Known valid people/places/institutions we want to keep
ALLOWLIST = {
    "édouard manet", "edouard manet",
    "paul gauguin", "rembrandt", "raphael",
    "paris", "london", "amsterdam", "florence",
    "italy", "france", "netherlands", "spain",
    "mexico", "japan", "united states",
    "louvre", "tate modern", "rijksmuseum",
    "british museum", "moma", "uffizi",
    "impressionism", "surrealism", "cubism",
    "post-impressionism", "renaissance",
}

def make_uri(label):
    """Convert a label to a safe URI, preserving accented characters."""
    label = label.strip()
    # Replace spaces with underscores
    label = re.sub(r"\s+", "_", label)
    # Remove characters that are not alphanumeric, underscore, or hyphen
    label = re.sub(r"[^\w\-]", "", label)
    return CAH[label]

def is_noisy(obj, predicate_str):
    """Filter out noisy extracted objects."""
    obj_clean = obj.strip()
    obj_lower = obj_clean.lower()

    # Always allow known good entities
    if obj_lower in ALLOWLIST:
        return False

    # Always block known bad entities
    if obj_lower in BLOCKLIST:
        return True

    # Too short
    if len(obj_clean) < 3:
        return True

    # Possessives
    if obj_lower.endswith("'s") or obj_lower.endswith("s'"):
        return True

    # Starts with "the "
    if obj_lower.startswith("the "):
        return True

    # Pure numbers or catalogue numbers like "4457 Van Gogh"
    if re.match(r"^\d+", obj_clean):
        return True

    # Contains only digits
    if re.match(r"^\d+$", obj_clean):
        return True

    # Very generic words that aren't entities
    generic_words = {"art", "work", "painting", "museum", "gallery",
                     "century", "period", "style", "school", "group"}
    if obj_lower in generic_words:
        return True

    # Wrong predicate-entity combinations
    if predicate_str == "createdBy" and any(
        word in obj_lower for word in ["museum", "gallery", "institute", "college"]
    ):
        return True

    if predicate_str == "heldBy" and re.match(r"^\d", obj_clean):
        return True

    return False

def main():
    print("=== Converting extracted triples to Turtle ===")

    g = Graph()
    g.bind("cah", CAH)
    g.bind("crm", CRM)
    g.bind("edm", EDM)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)

    total = 0
    skipped = 0
    seen_triples = set()

    with open(INPUT_FILE, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)

            predicate_str = record.get("predicate", "")
            subject_str   = record.get("subject", "")
            object_str    = record.get("object", "")
            entity_type   = record.get("entity_type", "")
            confidence    = record.get("confidence", 0.0)

            if confidence < 0.75:
                skipped += 1
                continue

            subject_uri = make_uri(subject_str)

            # Add rdf:type for subject
            if entity_type in CLASS_MAP:
                g.add((subject_uri, RDF.type, CLASS_MAP[entity_type]))

            # Handle datatype properties (dates)
            if predicate_str in DATATYPE_PREDICATE_MAP:
                year_match = re.search(r"\b(\d{4})\b", object_str)
                if year_match:
                    year = int(year_match.group(1))
                    predicate_uri = DATATYPE_PREDICATE_MAP[predicate_str]
                    triple_key = (str(subject_uri), str(predicate_uri), str(year))
                    if triple_key not in seen_triples:
                        seen_triples.add(triple_key)
                        g.add((subject_uri, predicate_uri,
                                Literal(f"{year}-01-01", datatype=XSD.date)))
                        total += 1
                else:
                    skipped += 1
                continue

            # Handle object properties
            if predicate_str not in PREDICATE_MAP:
                skipped += 1
                continue

            if is_noisy(object_str, predicate_str):
                skipped += 1
                continue

            predicate_uri = PREDICATE_MAP[predicate_str]
            object_uri = make_uri(object_str)

            triple_key = (str(subject_uri), str(predicate_uri), str(object_uri))
            if triple_key in seen_triples:
                skipped += 1
                continue
            seen_triples.add(triple_key)

            g.add((subject_uri, predicate_uri, object_uri))
            total += 1

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # Merge with seed triples if the file exists
    SEED_FILE = "data/unstructured/seed_triples.ttl"
    if os.path.exists(SEED_FILE):
        print("  Merging with seed triples...")
        seed_graph = Graph()
        seed_graph.parse(SEED_FILE, format="turtle")
        g += seed_graph
        print(f"  Seed triples added: {len(seed_graph)}")

    g.serialize(destination=OUTPUT_FILE, format="turtle")

    print(f"=== Done ===")
    print(f"    Triples written : {total}")
    print(f"    Triples skipped : {skipped}")
    print(f"    Output          : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()