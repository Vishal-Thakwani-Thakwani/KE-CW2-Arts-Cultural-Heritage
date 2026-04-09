"""
KG-RAG completion system for RDF/Turtle knowledge graphs.

Purpose
-------
Given:
- an RDF knowledge graph (.ttl) containing ontology + instances
- a JSON file listing missing gaps already identified

This script:
1. loads the KG
2. retrieves context from the KG for each missing gap
3. builds an LLM prompt using the retrieved KG facts
4. asks the LLM to propose a missing value
5. validates the proposal against ontology/domain/range/datatype constraints
6. optionally writes accepted triples back into the KG
7. saves:
   - an enriched Turtle graph
   - a JSON report of all completion attempts

Expected input files
--------------------
1) pipeline/merged_graphs.ttl (input KG; see CONFIG)
2) graph-completion/missing_gaps.json (see CONFIG)

Environment variables for LLM
-----------------------------
This script loads ``pipeline/.env`` and ``graph-completion/.env`` if present (without
overriding variables already set in the process environment).

Set either the LLM_* variables or the same OpenAI-style vars used by ``pipeline/kg_pipeline.py``:

- ``LLM_API_URL`` — chat completions URL (defaults to OpenAI if unset)
- ``LLM_API_KEY`` — or use ``OPENAI_API_KEY`` from ``pipeline/.env``
- ``LLM_MODEL`` — or use ``OPENAI_MODEL`` (default: gpt-4o-mini)

Example:

export LLM_API_URL="https://your-api-endpoint/v1/chat/completions"
export LLM_API_KEY="your_api_key"
export LLM_MODEL="your_model_name"

Rate limits (HTTP 429): ``call_llm`` retries with backoff. Optional env:
``LLM_MAX_HTTP_RETRIES`` (default 8), ``LLM_RETRY_BASE_SEC`` (default 1.0),
``LLM_GAP_DELAY_SEC`` (seconds between gaps; default 0).

Speed: ``LLM_MAX_TOKENS`` (default 384) shortens model generation time; ``LLM_HTTP_TIMEOUT_SEC``
(default 75) caps wait per request. Smaller retrieval: ``RAG_MAX_CONTEXT_LINES``,
``RAG_MAX_NEIGHBOR_TRIPLES``, ``RAG_MAX_SIMILAR_ENTITIES``, ``RAG_MAX_SIMILAR_ENTITY_TRIPLES``.

You can also adapt call_llm() to your provider.

Configuration
-------------
Edit the variables in the CONFIG section near the top of this file (paths, thresholds, flags).

Notes
-----
- This is a sample system, intended to be understandable and extensible.
- It uses the KG itself as the retrieval source, so this is a KG-based RAG pipeline.
- It is conservative by default: low-confidence or invalid outputs are rejected.
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path
import textwrap
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

import requests
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL, XSD
from rdflib.namespace import NamespaceManager


# -----------------------------
# CONFIG — edit these values
# -----------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
_PIPELINE = _REPO_ROOT / "pipeline"
_GRAPHCOMP = Path(__file__).resolve().parent


def _load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines into os.environ if the key is not already set."""
    if not path.is_file():
        return
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


_load_env_file(_PIPELINE / ".env")
_load_env_file(_GRAPHCOMP / ".env")

KG_PATH = str(_PIPELINE / "merged_graphs.ttl")
GAPS_PATH = str(_GRAPHCOMP / "missing_gaps.json")
OUT_TTL = str(_PIPELINE / "final_kg.ttl")
OUT_REPORT = str(_GRAPHCOMP / "rag_completion_report.json")
AUTO_ACCEPT_THRESHOLD = 0.80
INTERACTIVE = False
ADD_PROVENANCE = True


def _retry_wait_seconds(response: requests.Response, attempt: int, base_delay: float) -> float:
    """Sleep duration before retrying after 429/503. Honors Retry-After when present."""
    h = response.headers.get("Retry-After")
    if h:
        try:
            return min(float(h), 120.0)
        except ValueError:
            pass
    return min(base_delay * (2**attempt), 120.0)


# -----------------------------
# Data classes
# -----------------------------

@dataclass
class Gap:
    subject: str
    predicate: str
    kind: str  # "object_property" or "datatype_property"


@dataclass
class Candidate:
    raw_value: str
    parsed_type: str  # "uri", "literal", "unknown"
    confidence: float
    justification: str
    should_accept: bool
    validation_errors: List[str]
    final_value_repr: Optional[str] = None


@dataclass
class CompletionResult:
    subject: str
    predicate: str
    kind: str
    accepted: bool
    candidate: Candidate
    retrieved_context_size: int
    saved_triple: Optional[Tuple[str, str, str]] = None


# -----------------------------
# KG-RAG Completer
# -----------------------------

class KGRAGCompleter:
    def __init__(
        self,
        graph: Graph,
        namespace_manager: NamespaceManager,
        auto_accept_threshold: float = 0.80,
        add_provenance: bool = True,
        max_neighbor_triples: int = 25,
        max_similar_entities: int = 5,
        max_similar_entity_triples: int = 8,
        max_context_lines: int = 80,
    ) -> None:
        self.graph = graph
        self.ns = namespace_manager
        self.auto_accept_threshold = auto_accept_threshold
        self.add_provenance = add_provenance
        self.max_neighbor_triples = max_neighbor_triples
        self.max_similar_entities = max_similar_entities
        self.max_similar_entity_triples = max_similar_entity_triples
        self.max_context_lines = max_context_lines

        self.PROV = Namespace("http://www.w3.org/ns/prov#")
        self.EXMETA = Namespace("http://example.org/rag-meta/")
        self.graph.bind("prov", self.PROV)
        self.graph.bind("ragmeta", self.EXMETA)

    # -------------------------
    # Public API
    # -------------------------

    def complete_gap(self, gap: Gap, interactive: bool = False) -> CompletionResult:
        subject = URIRef(gap.subject)
        predicate = URIRef(gap.predicate)

        retrieved = self.retrieve_context(subject, predicate, gap.kind)
        prompt = self.build_prompt(subject, predicate, gap.kind, retrieved)
        llm_output = self.call_llm(prompt)
        candidate = self.parse_llm_output(llm_output, gap.kind)
        self.validate_candidate(subject, predicate, gap.kind, candidate)

        accepted = False
        saved_triple = None

        if candidate.confidence >= self.auto_accept_threshold and not candidate.validation_errors:
            candidate.should_accept = True

        if interactive:
            self.display_interactive_review(gap, retrieved, candidate)
            accepted = self.ask_user_accept(candidate)
        else:
            accepted = candidate.should_accept and not candidate.validation_errors

        if accepted:
            saved_triple = self.materialize_candidate(subject, predicate, gap.kind, candidate)
            if saved_triple and self.add_provenance:
                self.add_completion_provenance(subject, predicate, candidate, prompt)

        return CompletionResult(
            subject=gap.subject,
            predicate=gap.predicate,
            kind=gap.kind,
            accepted=accepted,
            candidate=candidate,
            retrieved_context_size=len(retrieved),
            saved_triple=saved_triple,
        )

    # -------------------------
    # Retrieval
    # -------------------------

    def retrieve_context(
        self,
        subject: URIRef,
        predicate: URIRef,
        kind: str,
    ) -> List[str]:
        """
        Retrieve context from the KG:
        1. all direct triples about subject
        2. inbound triples pointing to subject
        3. ontology/domain/range info for predicate
        4. similar entities of same rdf:type and some of their triples
        """
        lines: List[str] = []

        # Direct subject triples
        direct_triples = list(self.graph.triples((subject, None, None)))[: self.max_neighbor_triples]
        for s, p, o in direct_triples:
            lines.append(self.verbalize_triple(s, p, o))

        # Inbound triples
        inbound_triples = list(self.graph.triples((None, None, subject)))[: 10]
        for s, p, o in inbound_triples:
            lines.append(self.verbalize_triple(s, p, o))

        # Predicate ontology info
        lines.extend(self.retrieve_predicate_schema(predicate))

        # Similar entities
        similar_entities = self.find_similar_entities(subject, predicate)
        for sim in similar_entities[: self.max_similar_entities]:
            sim_lines = self.retrieve_entity_summary(sim)
            lines.append(f"Similar entity: {self.qname_or_uri(sim)}")
            lines.extend(sim_lines[: self.max_similar_entity_triples])

        # Deduplicate while preserving order
        seen = set()
        unique_lines = []
        for line in lines:
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)

        return unique_lines

    def retrieve_predicate_schema(self, predicate: URIRef) -> List[str]:
        lines: List[str] = []

        # Basic schema facts for predicate
        for _, _, o in self.graph.triples((predicate, RDF.type, None)):
            lines.append(f"Property type: {self.qname_or_uri(predicate)} rdf:type {self.qname_or_uri(o)}")

        for _, _, o in self.graph.triples((predicate, RDFS.domain, None)):
            lines.append(f"Property domain: {self.qname_or_uri(predicate)} domain {self.qname_or_uri(o)}")

        for _, _, o in self.graph.triples((predicate, RDFS.range, None)):
            lines.append(f"Property range: {self.qname_or_uri(predicate)} range {self.qname_or_uri(o)}")

        for _, _, o in self.graph.triples((predicate, RDFS.label, None)):
            lines.append(f"Property label: {self.literal_to_text(o)}")

        return lines

    def retrieve_entity_summary(self, entity: URIRef) -> List[str]:
        triples = list(self.graph.triples((entity, None, None)))[: self.max_neighbor_triples]
        return [self.verbalize_triple(s, p, o) for s, p, o in triples]

    def find_similar_entities(self, subject: URIRef, predicate: URIRef) -> List[URIRef]:
        """
        Very simple symbolic retrieval:
        - get rdf:type(s) of subject
        - retrieve other entities with same type
        - prefer ones that already have the missing predicate filled
        """
        subject_types = [o for _, _, o in self.graph.triples((subject, RDF.type, None)) if isinstance(o, URIRef)]
        candidates: List[URIRef] = []

        for t in subject_types:
            for s, _, _ in self.graph.triples((None, RDF.type, t)):
                if s == subject or not isinstance(s, URIRef):
                    continue
                # prefer entities with the missing predicate present
                if (s, predicate, None) in self.graph:
                    candidates.append(s)

        # Deduplicate
        seen = set()
        deduped = []
        for c in candidates:
            if c not in seen:
                deduped.append(c)
                seen.add(c)

        return deduped

    # -------------------------
    # Prompt building
    # -------------------------

    def build_prompt(
        self,
        subject: URIRef,
        predicate: URIRef,
        kind: str,
        retrieved_context: List[str],
    ) -> str:
        context_block = "\n".join(
            f"- {line}" for line in retrieved_context[: self.max_context_lines]
        )

        prompt = f"""
You are a knowledge graph completion assistant.

Task:
Predict ONE missing value for the triple:
({self.qname_or_uri(subject)}, {self.qname_or_uri(predicate)}, ?)

Rules:
1. Use ONLY the provided retrieved knowledge graph context.
2. Respect ontology/schema constraints if domain/range/datatype information is present.
3. If evidence is weak or insufficient, return UNKNOWN.
4. For object_property, prefer an existing entity URI already compatible with the graph.
5. For datatype_property, return a literal value only.
6. Be conservative. Do not invent unsupported facts.

Output JSON ONLY with this schema:
{{
  "value": "...",
  "value_type": "uri|literal|unknown",
  "confidence": 0.0,
  "justification": "short explanation"
}}

Missing predicate kind:
{kind}

Retrieved KG context:
{context_block}
"""
        return textwrap.dedent(prompt).strip()

    # -------------------------
    # LLM call
    # -------------------------

    def call_llm(self, prompt: str) -> str:
        """
        Calls an OpenAI-compatible chat completions endpoint.
        Adapt if your provider differs.
        """
        api_url = os.getenv("LLM_API_URL") or "https://api.openai.com/v1/chat/completions"
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        model = (
            os.getenv("LLM_MODEL")
            or os.getenv("OPENAI_MODEL")
            or "gpt-4o-mini"
        )

        if not api_key:
            raise RuntimeError(
                "Missing LLM API key. Set LLM_API_KEY or OPENAI_API_KEY "
                "(e.g. in pipeline/.env), or set LLM_API_URL for a non-OpenAI endpoint."
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": "Return strict JSON only. No markdown."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        max_tokens_raw = os.getenv("LLM_MAX_TOKENS", "384").strip()
        if max_tokens_raw:
            try:
                mt = int(max_tokens_raw)
                if mt > 0:
                    payload["max_tokens"] = mt
            except ValueError:
                pass

        http_timeout = float(os.getenv("LLM_HTTP_TIMEOUT_SEC", "75"))

        max_retries = max(1, int(os.getenv("LLM_MAX_HTTP_RETRIES", "8")))
        base_delay = float(os.getenv("LLM_RETRY_BASE_SEC", "1.0"))

        for attempt in range(max_retries):
            response = requests.post(
                api_url, headers=headers, json=payload, timeout=http_timeout
            )
            if response.status_code in (429, 503):
                if attempt + 1 >= max_retries:
                    response.raise_for_status()
                wait = _retry_wait_seconds(response, attempt, base_delay)
                time.sleep(wait)
                continue
            response.raise_for_status()
            data = response.json()
            try:
                return data["choices"][0]["message"]["content"]
            except Exception as exc:
                raise RuntimeError(f"Unexpected LLM response format: {data}") from exc

    # -------------------------
    # Parsing
    # -------------------------

    def parse_llm_output(self, llm_output: str, kind: str) -> Candidate:
        """
        Expects JSON like:
        {
          "value": "...",
          "value_type": "uri|literal|unknown",
          "confidence": 0.87,
          "justification": "..."
        }
        """
        validation_errors: List[str] = []

        try:
            payload = json.loads(llm_output)
        except json.JSONDecodeError:
            payload = {
                "value": "UNKNOWN",
                "value_type": "unknown",
                "confidence": 0.0,
                "justification": f"LLM output was not valid JSON: {llm_output[:300]}"
            }
            validation_errors.append("Invalid JSON returned by LLM.")

        raw_value = str(payload.get("value", "UNKNOWN")).strip()
        parsed_type = str(payload.get("value_type", "unknown")).strip().lower()
        justification = str(payload.get("justification", "")).strip()

        try:
            confidence = float(payload.get("confidence", 0.0))
        except Exception:
            confidence = 0.0
            validation_errors.append("Confidence was not numeric.")

        if parsed_type not in {"uri", "literal", "unknown"}:
            validation_errors.append(f"Invalid value_type: {parsed_type}")
            parsed_type = "unknown"

        if kind == "object_property" and parsed_type == "literal":
            validation_errors.append("Object property predicted a literal.")
        if kind == "datatype_property" and parsed_type == "uri":
            validation_errors.append("Datatype property predicted a URI.")

        return Candidate(
            raw_value=raw_value,
            parsed_type=parsed_type,
            confidence=confidence,
            justification=justification,
            should_accept=False,
            validation_errors=validation_errors,
        )

    # -------------------------
    # Validation
    # -------------------------

    def validate_candidate(
        self,
        subject: URIRef,
        predicate: URIRef,
        kind: str,
        candidate: Candidate,
    ) -> None:
        if candidate.parsed_type == "unknown" or candidate.raw_value.upper() == "UNKNOWN":
            candidate.validation_errors.append("LLM returned UNKNOWN.")
            return

        # Existing value check
        if (subject, predicate, None) in self.graph:
            candidate.validation_errors.append("Subject already has a value for this predicate in the KG.")

        # Domain validation
        domains = list(self.graph.objects(predicate, RDFS.domain))
        if domains:
            subject_types = set(self.graph.objects(subject, RDF.type))
            if not any(d in subject_types for d in domains):
                candidate.validation_errors.append(
                    f"Subject does not match predicate domain. Subject types: "
                    f"{[self.qname_or_uri(t) for t in subject_types]}, domains: "
                    f"{[self.qname_or_uri(d) for d in domains]}"
                )

        # Range validation
        ranges = list(self.graph.objects(predicate, RDFS.range))

        if kind == "object_property":
            if candidate.parsed_type != "uri":
                candidate.validation_errors.append("Expected URI for object property.")
                return

            obj = URIRef(candidate.raw_value)

            # If range exists, candidate should match at least one rdf:type
            if ranges:
                obj_types = set(self.graph.objects(obj, RDF.type))
                if not obj_types:
                    candidate.validation_errors.append(
                        f"Predicted URI has no rdf:type in the KG: {candidate.raw_value}"
                    )
                elif not any(r in obj_types for r in ranges):
                    candidate.validation_errors.append(
                        f"Predicted URI does not match predicate range. "
                        f"Object types: {[self.qname_or_uri(t) for t in obj_types]}, "
                        f"ranges: {[self.qname_or_uri(r) for r in ranges]}"
                    )

        elif kind == "datatype_property":
            if candidate.parsed_type != "literal":
                candidate.validation_errors.append("Expected literal for datatype property.")
                return

            # If range says xsd:string, xsd:integer, xsd:date etc., do basic parsing
            if ranges:
                datatype_ok = self.check_literal_against_ranges(candidate.raw_value, ranges)
                if not datatype_ok:
                    candidate.validation_errors.append(
                        f"Literal does not match predicate datatype range(s): "
                        f"{[self.qname_or_uri(r) for r in ranges]}"
                    )

    def check_literal_against_ranges(self, raw_value: str, ranges: List[URIRef]) -> bool:
        """
        Very lightweight datatype checking.
        """
        text = raw_value.strip().strip('"')

        for r in ranges:
            if r == XSD.string:
                return True
            if r == XSD.integer:
                try:
                    int(text)
                    return True
                except ValueError:
                    continue
            if r == XSD.decimal or r == XSD.float or r == XSD.double:
                try:
                    float(text)
                    return True
                except ValueError:
                    continue
            if r == XSD.boolean:
                if text.lower() in {"true", "false", "1", "0"}:
                    return True
            if r == XSD.date:
                # simple check: YYYY-MM-DD
                parts = text.split("-")
                if len(parts) == 3 and all(p.isdigit() for p in parts):
                    return True
            if r == RDFS.Literal:
                return True

        return False

    # -------------------------
    # Materialization
    # -------------------------

    def materialize_candidate(
        self,
        subject: URIRef,
        predicate: URIRef,
        kind: str,
        candidate: Candidate,
    ) -> Optional[Tuple[str, str, str]]:
        if candidate.validation_errors:
            return None

        if kind == "object_property":
            obj = URIRef(candidate.raw_value)
            self.graph.add((subject, predicate, obj))
            candidate.final_value_repr = self.qname_or_uri(obj)
            return (str(subject), str(predicate), str(obj))

        if kind == "datatype_property":
            literal = self.make_typed_literal(predicate, candidate.raw_value)
            self.graph.add((subject, predicate, literal))
            candidate.final_value_repr = literal.n3(self.ns)
            return (str(subject), str(predicate), str(literal))

        return None

    def make_typed_literal(self, predicate: URIRef, raw_value: str) -> Literal:
        ranges = list(self.graph.objects(predicate, RDFS.range))
        text = raw_value.strip().strip('"')

        for r in ranges:
            if r == XSD.string:
                return Literal(text, datatype=XSD.string)
            if r == XSD.integer:
                return Literal(int(text), datatype=XSD.integer)
            if r in {XSD.decimal, XSD.float, XSD.double}:
                return Literal(float(text), datatype=r)
            if r == XSD.boolean:
                val = text.lower() in {"true", "1"}
                return Literal(val, datatype=XSD.boolean)
            if r == XSD.date:
                return Literal(text, datatype=XSD.date)

        return Literal(text)

    def add_completion_provenance(
        self,
        subject: URIRef,
        predicate: URIRef,
        candidate: Candidate,
        prompt: str,
    ) -> None:
        event = URIRef(self.EXMETA[f"completion-{uuid.uuid4()}"])

        self.graph.add((event, RDF.type, self.EXMETA.RAGCompletionEvent))
        self.graph.add((event, self.EXMETA.completedSubject, subject))
        self.graph.add((event, self.EXMETA.completedPredicate, predicate))

        if candidate.parsed_type == "uri":
            self.graph.add((event, self.EXMETA.completedObject, URIRef(candidate.raw_value)))
        elif candidate.parsed_type == "literal":
            self.graph.add((event, self.EXMETA.completedLiteral, Literal(candidate.raw_value)))

        self.graph.add((event, self.EXMETA.confidence, Literal(candidate.confidence, datatype=XSD.decimal)))
        self.graph.add((event, self.EXMETA.justification, Literal(candidate.justification)))
        self.graph.add((event, self.EXMETA.method, Literal("KG-RAG with LLM")))
        self.graph.add((event, self.EXMETA.promptExcerpt, Literal(prompt[:1000])))
        self.graph.add((event, self.PROV.generatedAtTime, Literal(self.iso_now(), datatype=XSD.dateTime)))

    # -------------------------
    # Utility
    # -------------------------

    def verbalize_triple(self, s: URIRef, p: URIRef, o: Any) -> str:
        if isinstance(o, Literal):
            return f"{self.qname_or_uri(s)} {self.qname_or_uri(p)} {self.literal_to_text(o)}"
        return f"{self.qname_or_uri(s)} {self.qname_or_uri(p)} {self.qname_or_uri(o)}"

    def qname_or_uri(self, node: Any) -> str:
        try:
            return self.graph.namespace_manager.normalizeUri(node)
        except Exception:
            return str(node)

    def literal_to_text(self, lit: Literal) -> str:
        if lit.language:
            return f"\"{str(lit)}\"@{lit.language}"
        if lit.datatype:
            return f"\"{str(lit)}\"^^{self.qname_or_uri(lit.datatype)}"
        return f"\"{str(lit)}\""

    def iso_now(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    # -------------------------
    # Interactive review
    # -------------------------

    def display_interactive_review(self, gap: Gap, retrieved: List[str], candidate: Candidate) -> None:
        print("\n" + "=" * 80)
        print("GAP")
        print(f"Subject   : {gap.subject}")
        print(f"Predicate : {gap.predicate}")
        print(f"Kind      : {gap.kind}")

        print("\nRETRIEVED CONTEXT")
        for line in retrieved[:20]:
            print(f"  - {line}")

        print("\nLLM CANDIDATE")
        print(json.dumps({
            "value": candidate.raw_value,
            "value_type": candidate.parsed_type,
            "confidence": candidate.confidence,
            "justification": candidate.justification,
            "validation_errors": candidate.validation_errors
        }, indent=2))

    def ask_user_accept(self, candidate: Candidate) -> bool:
        if candidate.validation_errors:
            print("\nCandidate has validation errors and is rejected by default.")
            return False

        while True:
            choice = input("\nAccept this completion? [y/n]: ").strip().lower()
            if choice in {"y", "yes"}:
                return True
            if choice in {"n", "no"}:
                return False
            print("Please enter y or n.")


# -----------------------------
# File helpers
# -----------------------------

def load_graph(ttl_path: str) -> Graph:
    g = Graph()
    g.parse(ttl_path, format="turtle")
    return g


def load_gaps(json_path: str) -> List[Gap]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    gaps: List[Gap] = []
    for item in data:
        gaps.append(
            Gap(
                subject=item["subject"],
                predicate=item["predicate"],
                kind=item["kind"],
            )
        )
    return gaps


def save_report(results: List[CompletionResult], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2, ensure_ascii=False)


def print_summary(results: List[CompletionResult]) -> None:
    total = len(results)
    accepted = sum(1 for r in results if r.accepted)
    rejected = total - accepted

    print("\n" + "=" * 80)
    print("SUMMARY")
    print(f"Total gaps processed : {total}")
    print(f"Accepted completions : {accepted}")
    print(f"Rejected completions : {rejected}")

    if results:
        print("\nDETAIL")
        for r in results:
            status = "ACCEPTED" if r.accepted else "REJECTED"
            print(f"- {status}: ({r.subject}, {r.predicate}) -> {r.candidate.raw_value} "
                  f"[confidence={r.candidate.confidence:.2f}]")
            if r.candidate.validation_errors:
                for err in r.candidate.validation_errors:
                    print(f"    validation_error: {err}")


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    if not os.path.exists(KG_PATH):
        print(f"KG file not found: {KG_PATH}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(GAPS_PATH):
        print(f"Gaps file not found: {GAPS_PATH}", file=sys.stderr)
        sys.exit(1)

    graph = load_graph(KG_PATH)
    gaps = load_gaps(GAPS_PATH)

    completer = KGRAGCompleter(
        graph=graph,
        namespace_manager=graph.namespace_manager,
        auto_accept_threshold=AUTO_ACCEPT_THRESHOLD,
        add_provenance=ADD_PROVENANCE,
        max_neighbor_triples=int(os.getenv("RAG_MAX_NEIGHBOR_TRIPLES", "25")),
        max_similar_entities=int(os.getenv("RAG_MAX_SIMILAR_ENTITIES", "5")),
        max_similar_entity_triples=int(os.getenv("RAG_MAX_SIMILAR_ENTITY_TRIPLES", "8")),
        max_context_lines=int(os.getenv("RAG_MAX_CONTEXT_LINES", "80")),
    )

    results: List[CompletionResult] = []
    gap_delay = float(os.getenv("LLM_GAP_DELAY_SEC", "0"))

    for i, gap in enumerate(gaps, start=1):
        print(f"\nProcessing gap {i}/{len(gaps)}: ({gap.subject}, {gap.predicate})")
        t0 = time.perf_counter()
        try:
            result = completer.complete_gap(gap, interactive=INTERACTIVE)
            results.append(result)
            print(f"  completed in {time.perf_counter() - t0:.1f}s")
        except Exception as exc:
            failed_candidate = Candidate(
                raw_value="ERROR",
                parsed_type="unknown",
                confidence=0.0,
                justification=f"Exception while processing gap: {exc}",
                should_accept=False,
                validation_errors=[str(exc)],
            )
            results.append(
                CompletionResult(
                    subject=gap.subject,
                    predicate=gap.predicate,
                    kind=gap.kind,
                    accepted=False,
                    candidate=failed_candidate,
                    retrieved_context_size=0,
                    saved_triple=None,
                )
            )
            print(f"  failed after {time.perf_counter() - t0:.1f}s")

        if gap_delay > 0 and i < len(gaps):
            time.sleep(gap_delay)

    graph.serialize(destination=OUT_TTL, format="turtle")
    save_report(results, OUT_REPORT)
    print_summary(results)


if __name__ == "__main__":
    main()