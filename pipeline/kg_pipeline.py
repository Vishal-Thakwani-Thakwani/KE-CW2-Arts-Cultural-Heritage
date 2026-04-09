"""
Automated Pipeline for creation of Arts & Cultural Heritage Knowledge Graph

Pipeline Steps:
1. LLM-generated base ontology + complex relations
2. Data ingestion
3. RAG for missing elements
4. SPARQL queries

"""

import argparse
import csv
import json
import logging
import os
import re
import textwrap
import time
from datetime import datetime
from pathlib import Path

def timed_step(step_name, func, *args, **kwargs):
    start = time.perf_counter()
    print(f"Starting: {step_name}")

    result = func(*args, **kwargs)

    end = time.perf_counter()
    duration = end - start
    print(f"Finished: {step_name} in {duration:.2f} seconds\n")

    return result


try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from rdflib import Graph, Namespace, URIRef, Literal
    from rdflib.namespace import RDF, RDFS, OWL, XSD
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False

try:
    from SPARQLWrapper import SPARQLWrapper, JSON as SPARQL_JSON
    SPARQLWRAPPER_AVAILABLE = True
except ImportError:
    SPARQLWRAPPER_AVAILABLE = False

"""
PATHS
"""

ROOT = Path(__file__).parent.parent
PIPELINE_DIR = Path(__file__).parent
ONTOLOGY_DIR = ROOT / "ontology"
S_DATA_DIR = ROOT / "structured-data"
US_DATA_DIR = ROOT / "unstructured-data" 
SPARQL_DIR = ROOT / "queries" 
EXISTING_ONTS = ROOT / "ontology" / "existing_ontologies"
PROMPTS_FILE  = ROOT / "prompts" / "ontology_prompts" / "pipeline_prompt_1"
CR_PROMPTS_FILE = ROOT / "prompts" / "ontology_prompts" / "pipeline_prompt_2"

BASE_ONTOLOGY_FILE = ONTOLOGY_DIR / "cultural_heritage_ontology_1.ttl"
CR_ONTOLOGY_FILE = ONTOLOGY_DIR / "cultural_heritage_ontology_2.ttl"
POPULATED_ONTOLOGY_FILE = ONTOLOGY_DIR / "cultural_heritage_extended_kg.ttl"
RAG_ONTOLOGY_FILE = ONTOLOGY_DIR / "final_kg.ttl"
SPARQL_FILE = ROOT / "queries" / "sparql_queries.rq"
SPARQL_QUERIES_RESULTS_FILE = SPARQL_DIR / "sparql_results.csv"

"""
CONFIGURATION
"""

OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL     = "gpt-5.3"
SPARQL_ENDPOINT  = os.getenv("SPARQL_ENDPOINT", "http://localhost:3030/kg/sparql")

"""
LOGGING
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

"""
STEP 1: LLM-generated base ontology + complex relations
"""

def load_prompts() -> dict:
    if not PROMPTS_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPTS_FILE}")
    return PROMPTS_FILE.read_text(encoding="utf-8")

def load_existing_ontologies(path: Path) -> str:
    """Load the two existing files."""
    contents = []
    for file in path.glob("*.owl"):
        text = file.read_text(encoding="utf-8", errors="ignore")
        contents.append(f"# FILE: {file.name}\n{text}")

    if not contents:
        raise ValueError("No .owl files found in EXISTING_ONTS")

    return "\n\n".join(contents)

def load_ontology() -> str:
    return BASE_ONTOLOGY_FILE.read_text(encoding="utf-8")

def extract_turtle(raw: str) -> str:
    raw = re.sub(r"```(?:turtle|ttl|xml)?", "", raw)
    raw = raw.replace("```", "")
    return raw.strip()

def call_llm(prompt: str) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Output ONLY valid Turtle (TTL). No explanations."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()

def generate_ontology():
    print("Generating Arts and Cultural Heritage Ontology")

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set")

    #Load prompt
    prompt_template = load_prompt()

    #Load OWL ontologies
    existing_onts_text = load_existing_ontologies(EXISTING_ONTS)

    #Inject OWL into prompt
    final_prompt = f"""
    {prompt_template}
    Existing ontologies (OWL format):
    {existing_onts_text}
    """

    #Call LLM
    raw_output = call_llm(final_prompt)

    #Clean TTL
    ttl_output = extract_turtle(raw_output)

    #Save file
    BASE_ONTOLOGY_FILE.write_text(ttl_output, encoding="utf-8")

    print(f"Ontology generated successfully - Now adding complex relations")
    generate_ontology_cr()


def load_CR_prompt() -> dict:
    if not CR_PROMPTS_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {CR_PROMPTS_FILE}")
    return CR_PROMPTS_FILE.read_text(encoding="utf-8")

def generate_ontology_cr():
    print("Generating extended ontology with added complex relations")

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set")

    #Load prompt
    prompt_template = load_CR_prompt()

    #Load generated ontology
    generate_ontology_text = load_ontology()

    final_prompt = f"""
    {prompt_template}
    Generated Ontology:
    {generate_ontology_text}
    """

    #Call LLM
    raw_output = call_llm(final_prompt)

    #Clean TTL
    ttl_output = extract_turtle(raw_output)

    #Save file
    CR_ONTOLOGY_FILE.write_text(ttl_output, encoding="utf-8")

    print(f"Ontology with complex relations generated successfully")

"""
STEP 2: Data ingestion
"""

"""
STEP 3: RAG for missing elements
"""

"""
STEP 4: SPARQL queries
"""

def run_sparql_queries():
    if not SPARQL_FILE.exists():
        log.error(f"SPARQL file not found: {SPARQL_FILE}")
        return

    text = SPARQL_FILE.read_text(encoding="utf-8")

    #Split by lines that start with '# CQ' followed by a number and colon
    parts = re.split(r'(?=^# CQ\d+:)', text, flags=re.MULTILINE)
    prefix_block = ""
    queries = []
    for part in parts:
        if part.strip().startswith("# CQ"):
            #a query block
            full_query = prefix_block + part
            queries.append(full_query)
        else:
            #initial prefix block (PREFIX ... lines)
            prefix_block = part.strip()

    if not queries:
        log.error("No queries found (expected '# CQ1:', '# CQ2:', ...)")
        return

    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setReturnFormat(SPARQL_JSON)

    with open(SPARQL_QUERIES_RESULTS_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["# SPARQL Query Results"])
        writer.writerow([f"# Endpoint: {SPARQL_ENDPOINT}"])
        writer.writerow([f"# Execution time: {datetime.now().isoformat()}"])
        writer.writerow([])

        for idx, query in enumerate(queries, start=1):
            log.info(f"Executing query CQ{idx}...")
            try:
                sparql.setQuery(query)
                results = sparql.query().convert()

                #Extract the query name from the first comment line
                first_line = query.split('\n')[0].strip()
                query_name = first_line if first_line.startswith('# CQ') else f"CQ{idx}"

                writer.writerow([f"# {query_name}"])
                writer.writerow([f"# Query text: {query.split(chr(10))[0]} ..."])

                if "results" in results and "bindings" in results["results"]:
                    bindings = results["results"]["bindings"]
                    if bindings:
                        vars_list = list(bindings[0].keys())
                        writer.writerow([f"# Variables: {', '.join(vars_list)}"])
                        writer.writerow(vars_list)  # header
                        for binding in bindings:
                            row = [binding.get(var, {}).get("value", "") for var in vars_list]
                            writer.writerow(row)
                    else:
                        writer.writerow(["# No results returned."])
                else:
                    writer.writerow(["# Query did not return SELECT results (ASK/CONSTRUCT)."])
                    writer.writerow([f"# Raw response: {results}"])

                writer.writerow([])
                log.info(f"Query {query_name} finished.")

            except Exception as e:
                log.error(f"Query {query_name} failed: {e}")
                writer.writerow([f"# ERROR in {query_name}: {str(e)}"])
                writer.writerow([])
                continue

    log.info(f"All results saved to {SPARQL_QUERIES_RESULTS_FILE}")

if __name__ == "__main__":
    timed_step("Step 1: Generate base ontology + complex relations", generate_ontology)
    timed_step("Step 4: Run SPARQL queries", run_sparql_queries)
