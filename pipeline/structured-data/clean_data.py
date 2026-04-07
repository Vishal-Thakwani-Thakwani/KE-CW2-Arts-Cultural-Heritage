import json
import re
import time
import unicodedata
from datetime import datetime
from http.client import HTTPResponse
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"
DEPARTMENT_ID = 11  # Example: European Paintings
MAX_OBJECTS = 25

# The Met API returns 403 for urllib's default User-Agent; send a normal client UA.
# Referer can reduce CDN/WAF blocks. After many requests, 403/429 may occur — get_json retries with backoff.
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


def pretty_print(title: str, data: dict[str, Any]) -> None:
  print(f"\n=== {title} ===")
  print(json.dumps(data, indent=2)[:4000])


def normalize_string(value: str) -> str:
  text = unicodedata.normalize("NFKC", value)
  return re.sub(r"\s+", " ", text).strip()


def standardize_date(value: Any) -> Any:
  if isinstance(value, int):
    return value

  if not isinstance(value, str):
    return value

  text = normalize_string(value)
  if not text:
    return None

  # Keep simple year values as integers.
  if re.fullmatch(r"-?\d{1,4}", text):
    return int(text)

  # Normalize ISO timestamps and date values to YYYY-MM-DD.
  iso_candidate = text.replace("Z", "+00:00")
  try:
    dt = datetime.fromisoformat(iso_candidate)
    return dt.date().isoformat()
  except ValueError:
    return text


def is_nullish(value: Any) -> bool:
  if value is None:
    return True
  if isinstance(value, str) and value == "":
    return True
  if isinstance(value, (list, dict)) and len(value) == 0:
    return True
  return False


def dedupe_list(values: list[Any]) -> list[Any]:
  deduped: list[Any] = []
  seen: set[str] = set()

  for item in values:
    signature = json.dumps(item, sort_keys=True, ensure_ascii=False)
    if signature in seen:
      continue
    seen.add(signature)
    deduped.append(item)

  return deduped


def clean_value(value: Any, key: str | None = None) -> Any:
  if isinstance(value, str):
    value = normalize_string(value)
    if key and ("date" in key.lower() or "year" in key.lower()):
      value = standardize_date(value)
    if is_nullish(value):
      return None
    return value

  if isinstance(value, list):
    cleaned_items: list[Any] = []
    for item in value:
      cleaned_item = clean_value(item)
      if not is_nullish(cleaned_item):
        cleaned_items.append(cleaned_item)
    cleaned_items = dedupe_list(cleaned_items)
    return None if is_nullish(cleaned_items) else cleaned_items

  if isinstance(value, dict):
    cleaned_dict: dict[str, Any] = {}
    for child_key, child_value in value.items():
      cleaned_child = clean_value(child_value, key=child_key)
      if not is_nullish(cleaned_child):
        cleaned_dict[child_key] = cleaned_child
    return None if is_nullish(cleaned_dict) else cleaned_dict

  return value


def clean_record(record: dict[str, Any]) -> dict[str, Any]:
  cleaned = clean_value(record)
  return cleaned if isinstance(cleaned, dict) else {}


def get_department_object_ids(department_id: int, limit: int) -> list[int]:
  data = get_json(f"{BASE_URL}/objects?departmentIds={department_id}")
  object_ids = data.get("objectIDs") or []
  return object_ids[:limit]


def fetch_department_objects(department_id: int, limit: int) -> list[dict[str, Any]]:
  object_ids = get_department_object_ids(department_id, limit)
  objects: list[dict[str, Any]] = []

  for object_id in object_ids:
    obj = get_json(f"{BASE_URL}/objects/{object_id}")
    objects.append(obj)

  return objects


def dedupe_objects_by_id(objects: list[dict[str, Any]]) -> list[dict[str, Any]]:
  seen_ids: set[int] = set()
  deduped: list[dict[str, Any]] = []

  for obj in objects:
    object_id = obj.get("objectID")
    if not isinstance(object_id, int):
      continue
    if object_id in seen_ids:
      continue
    seen_ids.add(object_id)
    deduped.append(obj)

  return deduped


if __name__ == "__main__":
  raw_objects = fetch_department_objects(DEPARTMENT_ID, MAX_OBJECTS)
  cleaned_objects = [clean_record(obj) for obj in raw_objects]
  cleaned_deduped_objects = dedupe_objects_by_id(cleaned_objects)

  pretty_print(
    f"Cleaned objects sample (department={DEPARTMENT_ID})",
    {"count": len(cleaned_deduped_objects), "sample": cleaned_deduped_objects[:2]},
  )
