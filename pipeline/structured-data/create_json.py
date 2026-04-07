"""
Fetch Met Collection objects the same way as mapping.py: up to 5 per department
with unique normalized titles (same scan cap and rate limiting). Writes the
full API object payloads to a JSON file.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from mapping import (
  PAUSE_BETWEEN_DEPARTMENTS_SEC,
  TARGET_PER_DEPARTMENT,
  collect_unique_title_objects,
  fetch_departments,
)

# Written next to this script unless you change this path in __main__.
DEFAULT_OUT = Path(__file__).resolve().parent / "met_selected_by_department.json"


def build_payload(*, verbose: bool = True) -> dict[str, Any]:
  """For each department: select objects via mapping.py, return a dict ready for json.dump."""
  if verbose:
    print("Loading department list from Met API…")
  departments = fetch_departments()
  n_dep = len(departments)
  if verbose:
    print(f"Found {n_dep} departments. Fetching objects (up to {TARGET_PER_DEPARTMENT} unique titles each).\n")

  out_departments: list[dict[str, Any]] = []

  for i, dep in enumerate(departments, start=1):
    dep_id = dep["departmentId"]
    name = dep.get("displayName", "")
    if not isinstance(name, str):
      name = str(dep_id)
    if verbose:
      print(f"[{i}/{n_dep}] {name} (departmentId={dep_id})")

    # Full Met /objects/{id} JSON (same records mapping.py turns into RDF).
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

    # Match mapping.py: space out department batches to reduce API throttling.
    if PAUSE_BETWEEN_DEPARTMENTS_SEC > 0 and i < n_dep:
      if verbose:
        print(f"    Pausing {PAUSE_BETWEEN_DEPARTMENTS_SEC:.0f}s before next department (API cooldown)…\n")
      time.sleep(PAUSE_BETWEEN_DEPARTMENTS_SEC)

  total_objects = sum(len(d["objects"]) for d in out_departments)
  # Quick index of departments that did not reach TARGET_PER_DEPARTMENT (cap or sparse IDs).
  short = [
    d
    for d in out_departments
    if len(d["objects"]) < TARGET_PER_DEPARTMENT
  ]

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


if __name__ == "__main__":
  out_path = DEFAULT_OUT
  print("Met API → JSON (this may take several minutes).\n")
  payload = build_payload(verbose=True)
  out_path.parent.mkdir(parents=True, exist_ok=True)
  with out_path.open("w", encoding="utf-8") as f:
    # ensure_ascii=False keeps non-ASCII titles readable in the file.
    json.dump(payload, f, ensure_ascii=False, indent=2)
  print(f"Wrote {out_path}")
  print(f"Departments: {payload['totalDepartments']}, objects: {payload['totalObjects']}")
  below = payload["departmentsBelowTarget"]
  if below:
    print(f"Departments with fewer than {TARGET_PER_DEPARTMENT} objects (under scan cap): {len(below)}")
