# Arts and Cultural Heritage Knowledge Graph

**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2 (Group Project)  
**Domain:** Arts and Cultural Heritage  
**Institution:** King's College London  
**Academic Year:** 2025/26

## Current Status

> **Last updated:** 13 March 2026  
> **Phase:** Domain Analysis & Data Source Identification  
> **Next milestone:** Ontology modelling kickoff (Week 10)

## Project Overview

This project develops an automated **knowledge graph (KG)** for the **Arts and Cultural Heritage** domain. Unlike CW1, this is not a manually-built ontology — we must develop a computational system that automates as much of the KG construction process as possible, using LLMs, information extraction, existing KG APIs, and structured/unstructured data sources.

The KG will combine:
- At least **1 textual data source** and **1 structured data source** (JSON, XML, SQL, etc.)
- Extensions of at least **2 existing ontologies** (with 2+ subclasses and 2+ subproperties each)
- **20 competency questions** (10 manual + 10 LLM-generated)
- **20 SPARQL queries** answering those CQs
- **Completion analysis** with RAG to resolve gaps
- **Evaluation methodology** with quantitative metrics

## Team Roles

| Role | Member(s) | Responsibilities |
|------|-----------|------------------|
| **Domain Expert / Client** | Vishal Thakwani | Set objectives, domain decisions, lead 10 manual CQs, keep all documentation up to date |
| **Modelling Experts** (2) | TBC | Design ontology in Protégé, extend 2 existing ontologies, produce mappings, write queries/prompts, evaluation methodology |
| **Requirements, Data Ingestion & LLM Pipeline** (2) | TBC | Find and set up data sources, build extraction/processing code, data cleaning, produce mappings, develop LLM prompts |

## Repository Structure

```
.
├── README.md
├── domain-analysis/
│   ├── domain-expert-report.md      # Domain objectives, scope, concept sketch
│   ├── competency-questions.md      # 10 manual CQs (domain expert)
│   └── data-sources.md              # Domain-validated data source recommendations
├── ontology/
│   ├── domain-concept-sketch.md     # High-level domain concepts for modelling team
│   └── (ontology files built by modelling experts)
├── meetings/
│   ├── minutes-template.md          # Template for meeting minutes
│   ├── meeting-01.md                # Week 10 meeting (TBC)
│   ├── meeting-02.md                # Week 11 meeting (TBC)
│   └── meeting-03.md                # Week 12 meeting (TBC)
├── pipeline/
│   └── (data ingestion code built by pipeline team)
├── sparql/
│   └── (SPARQL queries built by modelling experts)
├── prompts/
│   └── (LLM prompts documented by all team members)
└── docs/
    ├── report.md                    # KG report (all contribute, domain expert maintains)
    └── completion-analysis.md        # KG completion analysis (TBC)
```

## Deliverables (from spec)

1. **Turtle file** of the KG (ontology + instances)
2. **Meeting minutes** (min. 3 meetings, weeks 10-12)
3. **KG Report** (intro, data sources, ontology extensions, mappings, queries, evaluation)
4. **Completion analysis** document (5 incomplete ontology + 5 incomplete instance elements, RAG strategy)
5. **Prompts document** (all LLM prompts and which KE task they belong to)
6. **Public code repository** (this repo)

## Marking Breakdown

| Criterion | Weight |
|-----------|--------|
| Classes and properties | 10 |
| Extensions of 2 existing ontologies | 5 |
| 20 competency questions (manual + LLM) | 10 |
| Data source mappings & pipeline | **25** |
| 20 SPARQL queries | 10 |
| KG completion + RAG | 10 |
| Prompts documentation | 10 |
| KG Report | **20** |
