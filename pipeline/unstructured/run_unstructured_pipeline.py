"""
Run the full unstructured data pipeline: fetch Wikipedia articles,
clean, chunk, extract NER triples, and convert to Turtle RDF.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from fetch_unstructured import main as fetch_unstructured
from clean_unstructured import main as clean_unstructured
from chunk_unstructured import main as chunk_unstructured
from extract_unstructured import main as extract_unstructured
from convert_to_turtle import main as convert_to_turtle

def run_unstructured_data_workflow():
    fetch_unstructured()
    clean_unstructured()
    chunk_unstructured()
    extract_unstructured()
    convert_to_turtle()

if __name__ == "__main__":
    raise SystemExit(run_unstructured_data_workflow())