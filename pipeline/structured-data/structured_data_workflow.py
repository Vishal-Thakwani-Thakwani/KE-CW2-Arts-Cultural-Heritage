"""
Run the full structured-data pipeline: fetch Met API JSON (create_json) then map to RDF (convert_json).
"""

from create_json import create_json
from convert_json import convert_json

def run_structured_data_workflow():
  create_json()
  convert_json()

if __name__ == "__main__":
  raise SystemExit(run_structured_data_workflow())