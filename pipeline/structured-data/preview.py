import json
from http.client import HTTPResponse
from typing import Any
from urllib.request import urlopen


BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"


def get_json(url: str) -> dict[str, Any]:
  with urlopen(url) as response:
    typed_response: HTTPResponse = response
    payload: bytes = typed_response.read()
    return json.loads(payload.decode("utf-8"))


# For formatting the output in the terminal
def pretty_print(title: str, data: dict[str, Any]) -> None:
  print(f"\n=== {title} ===")
  print(json.dumps(data, indent=2)[:4000])


if __name__ == "__main__":
  # List departments
  departments = get_json(f"{BASE_URL}/departments")
  pretty_print("Departments", departments)

  # Search for objects
  search = get_json(f"{BASE_URL}/search?q=sunflowers&hasImages=true")
  pretty_print("Search Results (sunflowers)", search)

  # Load one object from the search results (TESTING)
  if search.get("objectIDs"):
    object_id = search["objectIDs"][0]
    obj = get_json(f"{BASE_URL}/objects/{object_id}")
    pretty_print(f"Object {object_id}", obj)
  else:
    print("\nNo object IDs returned from search.")
