"""
Fetch Met Collection objects: up to TARGET_PER_DEPARTMENT (see helpers) per department
with unique (artist, normalised title) pairs (titles compared case-insensitively).
Writes full API object payloads to JSON (default met_art_objects.json).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from helpers import (
  PAUSE_BETWEEN_DEPARTMENTS_SEC,
  TARGET_PER_DEPARTMENT,
  collect_unique_title_objects,
  fetch_departments,
)

# Output from this stage feeds convert_json.py (same folder by default).
DEFAULT_OUT = Path(__file__).resolve().parent / "met_art_objects.json"


def build_payload(*, verbose: bool = True) -> dict[str, Any]:
  # Stage 1: all curatorial departments (Met /departments).
  if verbose:
    print("Loading department list from Met API…")
  departments = fetch_departments()
  n_dep = len(departments)
  if verbose:
    print(
      f"Found {n_dep} departments. Fetching objects (up to {TARGET_PER_DEPARTMENT} "
      f"unique artist+title pairs each).\n"
    )

  out_departments: list[dict[str, Any]] = []

  # Stage 2: per department, walk object IDs until we have enough distinct (artist, title) pairs
  # (title case-insensitive; or hit the scan cap — see helpers.collect_unique_title_objects).
  for i, dep in enumerate(departments, start=1):
    dep_id = dep["departmentId"]
    name = dep.get("displayName", "")
    if not isinstance(name, str):
      name = str(dep_id)
    if verbose:
      print(f"[{i}/{n_dep}] {name} (departmentId={dep_id})")

    selected = collect_unique_title_objects(dep_id, verbose=verbose)
    out_departments.append(
      {
        "departmentId": dep_id,
        "displayName": name,
        "objects": selected,
      }
    )

    if verbose:
      print(f"    → Stored {len(selected)} full object records for this department.\n")

    # Light throttling between departments to avoid Met API rate limits.
    if PAUSE_BETWEEN_DEPARTMENTS_SEC > 0 and i < n_dep:
      if verbose:
        print(f"    Pausing {PAUSE_BETWEEN_DEPARTMENTS_SEC:.0f}s before next department (API cooldown)…\n")
      time.sleep(PAUSE_BETWEEN_DEPARTMENTS_SEC)

  # Stage 3: wrap lists plus a small summary for sparse departments.
  total_objects = sum(len(d["objects"]) for d in out_departments)
  short = [d for d in out_departments if len(d["objects"]) < TARGET_PER_DEPARTMENT]

  return {
    "departments": out_departments,
    "totalDepartments": len(out_departments),
    "totalObjects": total_objects,
    "departmentsBelowTarget": [
      {
        "departmentId": d["departmentId"],
        "displayName": d["displayName"],
        "objectCount": len(d["objects"]),
      }
      for d in short
    ],
  }


def create_json():
  out_path = DEFAULT_OUT
  print("Met API → JSON (this may take several minutes).\n")
  payload = build_payload(verbose=True)
  
  # Full /objects/{id} documents as returned by the API (not a reduced schema).
  out_path.parent.mkdir(parents=True, exist_ok=True)
  with out_path.open("w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
  print(f"Wrote {out_path}")
  print(f"Departments: {payload['totalDepartments']}, objects: {payload['totalObjects']}")
  below = payload["departmentsBelowTarget"]
  if below:
    print(f"Departments with fewer than {TARGET_PER_DEPARTMENT} objects (under scan cap): {len(below)}")  


if __name__ == "__main__":
  raise SystemExit(create_json())
