from rdflib import Graph
import os

STRUCTURED_FILE = "pipeline/structured-data/rdf/structured_kg.ttl"
UNSTRUCTURED_FILE = "pipeline/unstructured/data/unstructured_triples.ttl"
OUTPUT_FILE = "data/final_knowledge_graph.ttl"

def merge_graphs():
    print("=== Merging knowledge graphs ===")
    g = Graph()

    input_files = [STRUCTURED_FILE, UNSTRUCTURED_FILE]

    for filepath in input_files:
        if os.path.exists(filepath):
            try:
                g.parse(filepath, format="turtle")
                print(f"Loaded: {filepath}")
            except Exception as e:
                print(f"ERROR parsing {filepath}: {e}")
        else:
            print(f"WARNING - file not found: {filepath}")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    g.serialize(destination=OUTPUT_FILE, format="turtle")

    print(f"Total triples: {len(g)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("=== Done ===")

if __name__ == "__main__":
    merge_graphs()