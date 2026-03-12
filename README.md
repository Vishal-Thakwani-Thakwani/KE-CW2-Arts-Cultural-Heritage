# Arts and Cultural Heritage Ontology

**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2 (Group Project)  
**Domain:** Arts and Cultural Heritage  
**Institution:** King's College London  
**Academic Year:** 2025/26

## Project Overview

This project develops an OWL2 ontology for the **Arts and Cultural Heritage** domain, covering artworks, artists, cultural institutions, exhibitions, conservation events, historical periods, and provenance. The ontology is grounded in the internationally standardised [CIDOC Conceptual Reference Model (CRM)](https://cidoc-crm.org/) (ISO 21127:2023) and is designed to be queried with SPARQL.

## Team Roles

| Role | Member(s) | Responsibilities |
|------|-----------|------------------|
| **Domain Expert** | Vishal Thakwani | Domain research, concept identification, competency questions, validation |
| **Modelling Expert** | TBC | Ontology design in Protégé, OWL2 axioms, defined classes |
| **Requirements, Data Integration & LLM Pipeline** | TBC (2 members) | Requirements engineering, data sourcing, LLM-assisted ontology generation |

## Repository Structure

```
.
├── README.md
├── domain-analysis/
│   ├── domain-expert-report.md      # Comprehensive domain analysis
│   ├── competency-questions.md      # 20 competency questions with rationale
│   └── data-sources.md              # LOD endpoints, APIs, existing ontologies
├── ontology/
│   ├── arts-cultural-heritage.ttl   # Manual OWL2 ontology (Turtle)
│   └── arts-cultural-heritage-ai.ttl # AI-generated ontology (TBC)
├── sparql/
│   └── queries.rq                   # SPARQL queries answering CQs (TBC)
├── prompts/
│   └── llm-prompts.txt              # LLM prompts used for AI ontology (TBC)
└── docs/
    └── reflection.pdf               # Group reflection document (TBC)
```

## Key Standards & References

- **CIDOC-CRM** (ISO 21127:2023) — The international standard ontology for cultural heritage documentation
- **Europeana Data Model (EDM)** — Metadata framework for Europe's digital cultural heritage
- **Linked Art** — A community and JSON-LD profile for describing art using CIDOC-CRM and Getty vocabularies
- **Getty Vocabularies** — AAT (Art & Architecture Thesaurus), ULAN (Union List of Artist Names), TGN (Thesaurus of Geographic Names)

## Getting Started

1. Clone this repository
2. Open `ontology/arts-cultural-heritage.ttl` in [Protégé](https://protege.stanford.edu/)
3. Run the HermiT or Pellet reasoner to classify the ontology
4. Execute SPARQL queries in `sparql/queries.rq` against the inferred model
