"""
Shared helpers for Met Collection API access and JSON → RDF mapping (cah: vocabulary).

Used by create_json.py and convert_json.py.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import unicodedata
from http.client import HTTPResponse
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# ---------------------------------------------------------------------------
# HTTP + string normalization (Met API)
# ---------------------------------------------------------------------------

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

# Browser-like UA: the Met API often rejects urllib’s default User-Agent with 403.
_MET_HEADERS = {
  "User-Agent": (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  ),
  "Accept": "application/json",
  "Accept-Language": "en-US,en;q=0.9",
  "Referer": "https://www.metmuseum.org/",
}


def get_json(
  url: str,
  *,
  max_retries: int = 8,
  base_delay_sec: float = 2.5,
  timeout_sec: float = 90.0,
) -> dict[str, Any]:

  # Exponential backoff on transient errors (403/429 and common gateway codes).
  delay = base_delay_sec
  last_error: BaseException | None = None
  for attempt in range(max_retries):
    req = Request(url, headers=_MET_HEADERS, method="GET")
    try:
      with urlopen(req, timeout=timeout_sec) as response:
        typed_response: HTTPResponse = response
        payload: bytes = typed_response.read()
        return json.loads(payload.decode("utf-8"))
    except HTTPError as e:
      last_error = e
      if e.code in (403, 429, 502, 503, 504) and attempt < max_retries - 1:
        time.sleep(delay)
        delay = min(delay * 1.75, 90.0)
        continue
      raise
    except URLError as e:
      last_error = e
      if attempt < max_retries - 1:
        time.sleep(delay)
        delay = min(delay * 1.75, 90.0)
        continue
      raise
  if last_error is not None:
    raise last_error
  raise RuntimeError("get_json: exhausted retries without error")


def normalize_string(value: str) -> str:

  # Used for title deduplication and readable RDF labels (whitespace + Unicode normalisation).
  text = unicodedata.normalize("NFKC", value)
  return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Met selection (per department)
# ---------------------------------------------------------------------------

TARGET_PER_DEPARTMENT = 3
MAX_FETCHES_PER_DEPARTMENT = 100
REQUEST_DELAY_SEC = 0.18
PAUSE_BETWEEN_DEPARTMENTS_SEC = 4.0

# Must match @prefix cah: in ontology/cultural_heritage_extended_kg.ttl.
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

  # Walk IDs in Met catalog order; keep the first object per normalised title until `target`
  # or until stop early due to `max_fetches` (limits API cost on huge departments).
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


# ---------------------------------------------------------------------------
# RDF: Met object JSON → cah: ABox (aligned with cultural_heritage_extended_kg.ttl)
# ---------------------------------------------------------------------------
# Stable fragment IDs from a hash of the label avoid illegal characters in URIs.

def _token(s: str) -> str:
  return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


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

  # Prefer aggregate display field; otherwise first constituent that looks like maker/artist.
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

  # Core identity & creators
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

  # Provenance: holding institution (defaults to The Met if field missing)
  repository = obj.get("repository")
  if isinstance(repository, str) and normalize_string(repository):
    inst_label = normalize_string(repository)
  else:
    inst_label = DEFAULT_REPOSITORY
  inst = institution_uri(inst_label)
  g.add((inst, RDF.type, CAH.Institution))
  g.add((inst, RDFS.label, Literal(inst_label, lang="en")))
  g.add((artwork, CAH.heldBy, inst))

  # Materials / classification / period / begin year (when present and valid)
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
