"""
Map Met Collection API JSON to instance RDF using the cah: vocabulary from
ontology/cultural_heritage_extended_kg.ttl (ABox only; load alongside the ontology).

Selects up to 5 objects per department with unique normalized titles (API object
order, scan capped per department).
"""

from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from typing import Any

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from clean_data import BASE_URL, get_json, normalize_string

TARGET_PER_DEPARTMENT = 5
MAX_FETCHES_PER_DEPARTMENT = 500
# Space requests to reduce Met API 403 / rate limits (see clean_data.get_json retries).
REQUEST_DELAY_SEC = 0.18
PAUSE_BETWEEN_DEPARTMENTS_SEC = 4.0

CAH = Namespace("http://example.org/culturalheritage#")


def title_uniqueness_key(title: str) -> str:
  normalized = normalize_string(title)
  return normalized.casefold()


def fetch_departments() -> list[dict[str, Any]]:
  data = get_json(f"{BASE_URL}/departments")
  raw = data.get("departments") or []
  return [d for d in raw if isinstance(d.get("departmentId"), int)]


def fetch_object_ids_for_department(department_id: int) -> list[int]:
  data = get_json(f"{BASE_URL}/objects?departmentIds={department_id}")
  raw_ids = data.get("objectIDs") or []
  return [int(oid) for oid in raw_ids if oid is not None]


def fetch_object(object_id: int) -> dict[str, Any]:
  if REQUEST_DELAY_SEC > 0:
    time.sleep(REQUEST_DELAY_SEC)
  return get_json(f"{BASE_URL}/objects/{object_id}")


def _preview_text(text: str, max_len: int = 56) -> str:
  t = normalize_string(text)
  if len(t) <= max_len:
    return t
  return t[: max_len - 1] + "…"


def collect_unique_title_objects(
  department_id: int,
  target: int = TARGET_PER_DEPARTMENT,
  max_fetches: int = MAX_FETCHES_PER_DEPARTMENT,
  *,
  verbose: bool = False,
) -> list[dict[str, Any]]:
  ids = fetch_object_ids_for_department(department_id)
  seen_titles: set[str] = set()
  selected: list[dict[str, Any]] = []
  fetches = 0
  fetch_failures = 0

  if verbose:
    print(f"    Catalog: {len(ids)} object IDs (scan cap {max_fetches} fetches, want {target} unique titles).")

  for oid in ids:
    if len(selected) >= target or fetches >= max_fetches:
      break
    fetches += 1
    if verbose and fetches > 1 and fetches % 25 == 0:
      print(f"    … {fetches} fetches — kept {len(selected)}/{target} unique titles so far.")
    try:
      obj = fetch_object(oid)
    except OSError as err:
      fetch_failures += 1
      if verbose and fetch_failures <= 3:
        print(f"    ! object {oid}: fetch failed after retries ({err!r}).")
      elif verbose and fetch_failures == 4:
        print("    ! (further per-object failures omitted; totals at end of department.)")
      continue
    title = obj.get("title")
    if not isinstance(title, str):
      continue
    if not normalize_string(title):
      continue
    key = title_uniqueness_key(title)
    if key in seen_titles:
      continue
    seen_titles.add(key)
    selected.append(obj)
    if verbose:
      print(f"    + [{len(selected)}/{target}] object {oid}: {_preview_text(title)!r}")

  if verbose:
    hit_cap = fetches >= max_fetches and len(selected) < target
    note = f" (hit {max_fetches}-fetch cap)" if hit_cap else ""
    print(f"    Finished department {department_id}: {len(selected)} objects in {fetches} fetches{note}.")
    if fetch_failures:
      print(f"    Object fetches that failed (after API retries): {fetch_failures}.")

  return selected


def _token(s: str) -> str:
  digest = hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]
  return digest


def _slug_part(text: str, max_len: int = 48) -> str:
  slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
  if len(slug) > max_len:
    slug = slug[:max_len]
  return slug or "x"


def artist_uri_for_display_name(name: str) -> URIRef:
  normalized = normalize_string(name)
  return CAH[f"artist_{_slug_part(normalized)}_{_token(normalized)}"]


def institution_uri(repository: str) -> URIRef:
  normalized = normalize_string(repository)
  return CAH[f"institution_{_token(normalized)}"]


def medium_uri(label: str) -> URIRef:
  normalized = normalize_string(label)
  return CAH[f"medium_{_token(normalized)}"]


def genre_uri(label: str) -> URIRef:
  normalized = normalize_string(label)
  return CAH[f"genre_{_token(normalized)}"]


def period_uri(label: str) -> URIRef:
  normalized = normalize_string(label)
  return CAH[f"period_{_token(normalized)}"]


UNKNOWN_ARTIST = CAH["artist_unknown"]
DEFAULT_REPOSITORY = "The Metropolitan Museum of Art"


def ensure_unknown_artist(g: Graph) -> None:
  g.add((UNKNOWN_ARTIST, RDF.type, CAH.Artist))
  g.add((UNKNOWN_ARTIST, RDFS.label, Literal("Unknown artist", lang="en")))


def creation_date_literal(begin: Any) -> Literal | None:
  if not isinstance(begin, int):
    return None
  if not (1 <= begin <= 9999):
    return None
  return Literal(f"{begin:04d}-01-01", datatype=XSD.date)


def primary_artist_name(obj: dict[str, Any]) -> str | None:
  name = obj.get("artistDisplayName")
  if isinstance(name, str) and normalize_string(name):
    return normalize_string(name)
  constituents = obj.get("constituents")
  if not isinstance(constituents, list):
    return None
  for c in constituents:
    if not isinstance(c, dict):
      continue
    role = c.get("role")
    nm = c.get("name")
    if not isinstance(nm, str) or not normalize_string(nm):
      continue
    if isinstance(role, str):
      rl = role.lower()
      if any(k in rl for k in ("artist", "maker", "attributed")):
        return normalize_string(nm)
  return None


def add_object_to_graph(g: Graph, obj: dict[str, Any]) -> None:
  oid = obj.get("objectID")
  if not isinstance(oid, int):
    return

  artwork = CAH[f"met_object_{oid}"]
  g.add((artwork, RDF.type, CAH.Artwork))

  title = obj.get("title")
  if isinstance(title, str) and normalize_string(title):
    g.add((artwork, RDFS.label, Literal(normalize_string(title), lang="en")))

  artist_name = primary_artist_name(obj)
  if artist_name:
    artist = artist_uri_for_display_name(artist_name)
    g.add((artist, RDF.type, CAH.Artist))
    g.add((artist, RDFS.label, Literal(artist_name, lang="en")))
    g.add((artwork, CAH.createdBy, artist))
  else:
    ensure_unknown_artist(g)
    g.add((artwork, CAH.createdBy, UNKNOWN_ARTIST))

  repository = obj.get("repository")
  if isinstance(repository, str) and normalize_string(repository):
    inst_label = normalize_string(repository)
  else:
    inst_label = DEFAULT_REPOSITORY
  inst = institution_uri(inst_label)
  g.add((inst, RDF.type, CAH.Institution))
  g.add((inst, RDFS.label, Literal(inst_label, lang="en")))
  g.add((artwork, CAH.heldBy, inst))

  medium = obj.get("medium")
  if isinstance(medium, str) and normalize_string(medium):
    for part in re.split(r"\s*,\s*", medium):
      token = normalize_string(part)
      if not token:
        continue
      m = medium_uri(token)
      g.add((m, RDF.type, CAH.Medium))
      g.add((m, RDFS.label, Literal(token, lang="en")))
      g.add((artwork, CAH.usesMedium, m))

  classification = obj.get("classification")
  if isinstance(classification, str) and normalize_string(classification):
    cl = normalize_string(classification)
    gn = genre_uri(cl)
    g.add((gn, RDF.type, CAH.Genre))
    g.add((gn, RDFS.label, Literal(cl, lang="en")))
    g.add((artwork, CAH.hasGenre, gn))

  period = obj.get("period")
  if isinstance(period, str) and normalize_string(period):
    pl = normalize_string(period)
    pn = period_uri(pl)
    g.add((pn, RDF.type, CAH.ArtPeriod))
    g.add((pn, RDFS.label, Literal(pl, lang="en")))
    g.add((artwork, CAH.createdInPeriod, pn))

  date_lit = creation_date_literal(obj.get("objectBeginDate"))
  if date_lit is not None:
    g.add((artwork, CAH.hasCreationDate, date_lit))


def build_graph_for_all_departments(*, verbose: bool = True) -> tuple[Graph, list[tuple[int, str, int]]]:
  """
  Returns the graph and a list of (departmentId, displayName, count_selected).
  """
  g = Graph()
  g.bind("cah", CAH)
  g.bind("rdfs", RDFS)
  g.bind("rdf", RDF)
  g.bind("xsd", XSD)

  summary: list[tuple[int, str, int]] = []
  if verbose:
    print("Loading department list from Met API…")
  departments = fetch_departments()
  n_dep = len(departments)
  if verbose:
    print(f"Found {n_dep} departments. Starting object fetch and mapping.\n")

  for i, dep in enumerate(departments, start=1):
    dep_id = dep["departmentId"]
    name = dep.get("displayName", "")
    if not isinstance(name, str):
      name = str(dep_id)
    if verbose:
      print(f"[{i}/{n_dep}] {name} (departmentId={dep_id})")
    triples_before = len(g)
    selected = collect_unique_title_objects(dep_id, verbose=verbose)
    for obj in selected:
      add_object_to_graph(g, obj)
    summary.append((dep_id, name, len(selected)))
    if verbose:
      added = len(g) - triples_before
      print(f"    → Added {added} triples for this department ({len(g)} triples in graph total).\n")
    if PAUSE_BETWEEN_DEPARTMENTS_SEC > 0 and i < n_dep:
      if verbose:
        print(f"    Pausing {PAUSE_BETWEEN_DEPARTMENTS_SEC:.0f}s before next department (API cooldown)…\n")
      time.sleep(PAUSE_BETWEEN_DEPARTMENTS_SEC)

  return g, summary


if __name__ == "__main__":
  print("Met → cah: ontology mapping (this may take several minutes).\n")
  graph, dept_summary = build_graph_for_all_departments(verbose=True)
  rdf_dir = Path(__file__).resolve().parent / "rdf"
  rdf_dir.mkdir(parents=True, exist_ok=True)
  out_path = rdf_dir / "met_mapped_by_department.ttl"
  print(f"Serializing graph to {out_path}…")
  graph.serialize(destination=out_path, format="turtle")
  print("Done serializing.\n")

  total_objects = sum(c for _, _, c in dept_summary)
  short = [(did, name, c) for did, name, c in dept_summary if c < TARGET_PER_DEPARTMENT]

  print("— Summary —")
  print(f"Wrote {len(graph)} triples to {out_path}")
  print(f"Departments processed: {len(dept_summary)}")
  print(f"Total objects mapped: {total_objects}")
  if short:
    print(f"Departments with fewer than {TARGET_PER_DEPARTMENT} objects (under scan cap):")
    for did, name, c in short:
      print(f"  {did} {name!r}: {c}")
