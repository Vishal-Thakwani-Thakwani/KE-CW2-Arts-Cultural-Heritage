"""
Merge unstructured and structured pipeline Turtle outputs into one graph.
Run after run_unstructured_pipeline.py and structured_data_workflow.py.
"""

from pathlib import Path

from rdflib import Graph

_REPO_ROOT = Path(__file__).resolve().parent.parent
UNSTRUCTURED_TTL = _REPO_ROOT / "pipeline" / "unstructured" / "data" / "unstructured_triples.ttl"
STRUCTURED_TTL = _REPO_ROOT / "pipeline" / "structured-data" / "rdf" / "structured_kg.ttl"
MERGED_OUT = _REPO_ROOT / "pipeline" / "merged_graphs.ttl"


def main() -> None:
    g = Graph()
    for path in (UNSTRUCTURED_TTL, STRUCTURED_TTL):
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing input graph: {path}. Run the unstructured and structured pipelines first."
            )
        g.parse(path, format="turtle")
    MERGED_OUT.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=MERGED_OUT, format="turtle")
    print(f"Wrote merged graph to {MERGED_OUT}")


if __name__ == "__main__":
    main()
