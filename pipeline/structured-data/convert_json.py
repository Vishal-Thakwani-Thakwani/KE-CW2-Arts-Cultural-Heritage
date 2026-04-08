"""
Map department-grouped Met JSON (default: met_data.json) into the extended ontology
(ontology/cultural_heritage_extended_kg.ttl) using the cah: ABox mapping in helpers.

TBox (classes/properties) comes from the ontology file; instance triples are added in
helpers.add_object_to_graph, optionally plus dcterms:subject for curatorial department.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from rdflib import Graph, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD

from helpers import CAH, add_object_to_graph

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_DEFAULT_JSON = _SCRIPT_DIR / "met_data.json"
_DEFAULT_ONTOLOGY = _REPO_ROOT / "ontology" / "cultural_heritage_extended_kg.ttl"
_DEFAULT_OUT = _SCRIPT_DIR / "rdf" / "complete_cultural_heritage_kg.ttl"


def load_department_payload(path: Path) -> dict[str, Any]:
  # Expected shape: { "departments": [ { "displayName", "objects": [ ... ] }, ... ] }
  with path.open("r", encoding="utf-8") as f:
    data = json.load(f)
  if not isinstance(data, dict) or "departments" not in data:
    raise ValueError(f"Expected JSON object with 'departments' key: {path}")
  return data


def iter_objects(data: dict[str, Any]):
  # Flatten to (department label, object dict) pairs for mapping + optional subject link.
  for dept in data.get("departments") or []:
    if not isinstance(dept, dict):
      continue
    display_name = dept.get("displayName")
    dept_label = display_name if isinstance(display_name, str) else None
    for obj in dept.get("objects") or []:
      if isinstance(obj, dict):
        yield dept_label, obj


def attach_department_subject(g: Graph, obj: dict[str, Any], dept_display_name: str | None) -> None:
  # Curatorial department is grouping metadata from create_json, not in the Met record alone.
  if not dept_display_name or not str(dept_display_name).strip():
    return
  oid = obj.get("objectID")
  if not isinstance(oid, int):
    return
  artwork = CAH[f"met_object_{oid}"]
  lit = str(dept_display_name).strip()
  g.add((artwork, DCTERMS.subject, Literal(lit, lang="en")))


def build_graph(
  data: dict[str, Any],
  *,
  ontology_path: Path | None,
  link_department: bool,
) -> tuple[Graph, int]:
  g = Graph()
  g.bind("cah", CAH)
  g.bind("rdfs", RDFS)
  g.bind("rdf", RDF)
  g.bind("xsd", XSD)
  g.bind("dcterms", DCTERMS)

  # When None (--instances-only), emit ABox only; otherwise TBox + ABox in one graph.
  if ontology_path is not None:
    g.parse(str(ontology_path), format="turtle")

  count = 0
  for dept_label, obj in iter_objects(data):
    add_object_to_graph(g, obj)
    if link_department:
      attach_department_subject(g, obj, dept_label)
    if isinstance(obj.get("objectID"), int):
      count += 1
  return g, count


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(description="Map Met JSON (by department) to cah: RDF with ontology.")
  parser.add_argument(
    "--input",
    type=Path,
    default=_DEFAULT_JSON,
    help="Path to Met JSON (default: met_data.json next to this script)",
  )
  parser.add_argument(
    "--ontology",
    type=Path,
    default=_DEFAULT_ONTOLOGY,
    help="Path to cultural_heritage_extended_kg.ttl (--instances-only skips loading it)",
  )
  parser.add_argument(
    "--output",
    type=Path,
    default=None,
    help="Output Turtle (default: rdf/complete_cultural_heritage_kg.ttl or rdf/met_instances_only.ttl)",
  )
  parser.add_argument(
    "--instances-only",
    action="store_true",
    help="Do not load the ontology; emit only ABox triples",
  )
  parser.add_argument(
    "--no-department-subject",
    action="store_true",
    help="Do not add dcterms:subject from JSON department displayName",
  )
  args = parser.parse_args(argv)

  if not args.input.is_file():
    print(f"Input JSON not found: {args.input}", file=sys.stderr)
    return 1
  if not args.instances_only and not args.ontology.is_file():
    print(f"Ontology file not found: {args.ontology}", file=sys.stderr)
    return 1

  data = load_department_payload(args.input)
  onto = None if args.instances_only else args.ontology
  
  # Default output path depends on whether the ontology Turtle is merged in.
  if args.output is None:
    out = _SCRIPT_DIR / "rdf" / "met_instances_only.ttl" if onto is None else _DEFAULT_OUT
  else:
    out = args.output

  g, n_objects = build_graph(
    data,
    ontology_path=onto,
    link_department=not args.no_department_subject,
  )
  out.parent.mkdir(parents=True, exist_ok=True)
  g.serialize(destination=str(out), format="turtle")
  print(f"Wrote {len(g)} triples ({n_objects} objects) → {out}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
