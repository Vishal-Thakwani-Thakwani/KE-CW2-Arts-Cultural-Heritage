"""
Load the first 20 Met Museum objects in department 1 (same API base as preview.py)
and materialise RDF with PySPARQL Anything (Facade-X). Requires a JDK and JAVA_HOME.
"""

import json
import tempfile
from http.client import HTTPResponse
from pathlib import Path
from typing import Any, TextIO
from urllib.request import urlopen

import pysparql_anything as sa
from rdflib import Graph

# Met Collection API
BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"
DEPARTMENT_ID = 1
SAMPLE_SIZE = 20


def get_json(url: str) -> dict[str, Any]:
  """Fetch one JSON document from the Met Collection API."""

  with urlopen(url) as response:
    typed_response: HTTPResponse = response
    return json.loads(typed_response.read().decode("utf-8"))


def load_department_objects(department_id: int, limit: int) -> list[dict[str, Any]]:
  '''Load the objects for a given department and return a list of dictionaries.'''

  listing: dict[str, Any] = get_json(f"{BASE_URL}/objects?departmentIds={department_id}")
  raw_ids: list[Any] = listing.get("objectIDs") or []
  ids: list[int] = [int(oid) for oid in raw_ids[:limit]]

  # One request per object: full records for SPARQL Anything.
  return [get_json(f"{BASE_URL}/objects/{oid}") for oid in ids]


def json_to_rdf_graph(json_path: Path) -> Graph:
  '''Convert a JSON file to an RDF graph using SPARQL Anything.'''

  # SPARQL Anything reads the file URI and maps JSON to triples via the Facade-X SERVICE block.
  engine: sa.SparqlAnything = sa.SparqlAnything()
  location: str = json_path.resolve().as_uri()
  query: str = f"""
  PREFIX fx: <http://sparql.xyz/facade-x/ns/>
  PREFIX xyz: <http://sparql.xyz/facade-x/data/>
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  PREFIX ex: <http://example.org/met/>

  CONSTRUCT {{
    # This creates an 'Individual' for every object in the JSON list
    ?objectURI rdf:type ex:Artwork ;
              rdfs:label ?title ;
              ex:hasArtist ?artist ;
              ex:objectID ?id .
  }}
  WHERE {{
    SERVICE <x-sparql-anything:location={location}> {{
      # Navigate the JSON structure: payload -> objects -> [list items]
      ?root xyz:objects ?container .
      ?container ?slot ?item .
      
      # Extract specific fields
      ?item xyz:title ?title .
      ?item xyz:objectID ?id .
      OPTIONAL {{ ?item xyz:artistDisplayName ?artist }}
      
      # Create a nice URI for Protégé to display
      BIND(IRI(CONCAT("http://example.org/met/art_", STR(?id))) AS ?objectURI)
    }}
  }}
  """
  graph: Graph = engine.construct(query=query)
  return graph


if __name__ == "__main__":
  objects: list[dict[str, Any]] = load_department_objects(DEPARTMENT_ID, SAMPLE_SIZE)
  payload: dict[str, Any] = {"departmentId": DEPARTMENT_ID, "objects": objects}

  # Write the payload to a temporary file.
  with tempfile.NamedTemporaryFile(
    mode="w",
    suffix=".json",
    delete=False,
    encoding="utf-8",
  ) as tmp:
    tmp_file: TextIO = tmp
    json.dump(payload, tmp_file, ensure_ascii=False)
    tmp_path = Path(tmp.name)

  # Convert the JSON to an RDF graph.
  graph: Graph
  try:
    graph = json_to_rdf_graph(tmp_path)
  finally:
    tmp_path.unlink(missing_ok=True)

  # Write the RDF graph to a file.
  rdf_dir = Path(__file__).resolve().parent / "rdf"
  rdf_dir.mkdir(parents=True, exist_ok=True)
  out = rdf_dir / "department1_objects_20.ttl"
  graph.serialize(destination=out, format="turtle")
  print(f"Wrote {len(graph)} triples to {out}")
