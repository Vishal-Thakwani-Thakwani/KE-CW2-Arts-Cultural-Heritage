# Arts and Cultural Heritage Knowledge Graph — Report

**Created by:** Vishal Thakwani, Oluwatamilore Oshinnaike, Jia Er Tee, Hristina Georgieva, Yusuf Rahman
**GitHub Repo:** https://github.com/Vishal-Thakwani-Thakwani/KE-CW2-Arts-Cultural-Heritage

---

## Introduction

This project develops an automated knowledge graph (KG) for the Arts and Cultural Heritage domain, covering the realm of visual art objects and their real-world relationships. Core entity types include artworks (paintings, sculptures, photographs), agents (artists, curators, collectors), cultural institutions (museums, galleries), events (exhibitions, conservation, provenance transfers), and classificatory concepts (art periods, movements, genres, mediums). The scope is deliberately limited to visual arts, excluding performing arts such as music, theatre, and dance, to keep the KG focused and manageable for a team of five.

The primary objective is to design and implement an automated pipeline that constructs both an ontology and a populated knowledge graph, supporting structured representation and SPARQL querying of cultural heritage data. The pipeline ingests one structured and one unstructured data source, extends two existing ontologies (CIDOC-CRM and the Europeana Data Model), and uses LLM-assisted techniques at multiple stages — from ontology generation to competency question augmentation and data extraction. The project is motivated by real-world practice: GLAMs (Galleries, Libraries, Archives, Museums) are actively investing in knowledge graphs for cross-institutional discovery and digital preservation, making this domain both practically relevant and technically rich.

## Data Source Selection

**Structured source — Metropolitan Museum of Art API.** The Met's open-access REST API provides over 470,000 artwork records in JSON format with no authentication required (CC0 licence). Each record includes fields such as title, artistDisplayName, objectDate, medium, department, classification, period, and country. We sampled up to five objects per curatorial department, yielding 95 unique-title objects that span 5,000 years of art across 19 departments. The sampling script (`create_json.py`) applies title-deduplication and exponential-backoff retry logic against the Met's rate limits.

**Unstructured source — Wikipedia.** We selected 13 Wikipedia articles covering 5 notable artists (Leonardo da Vinci, Claude Monet, Frida Kahlo, Vincent van Gogh, Yayoi Kusama), 5 iconic artworks (Mona Lisa, Water Lilies, The Night Watch, Guernica, My Bed), and 3 major museums (the Louvre, Tate Modern, the British Museum). These entities were chosen because they have well-documented Wikipedia pages containing rich biographical, provenance, and institutional information. Articles were fetched via the Wikipedia API, cleaned of citation markers and wiki-formatting, split into named sections (biography, career, legacy, works, exhibitions), and chunked into ≤500-character segments for NER processing.

## Extension of Existing Ontologies

The two ontologies selected for extension are CIDOC-CRM (ISO 21127) and the Europeana Data Model (EDM). CIDOC-CRM is the international standard for cultural heritage documentation, providing a rich event-centric class hierarchy. EDM was designed for cross-institutional cultural heritage aggregation and interoperates naturally with CIDOC-CRM.

Our custom namespace (`cah:`) introduces 21 classes and over 30 object/datatype properties. Subclass extensions of CIDOC-CRM include `cah:Artist rdfs:subClassOf crm:E21_Person`, `cah:Artwork rdfs:subClassOf crm:E22_Man-Made_Object`, `cah:Exhibition rdfs:subClassOf crm:E7_Activity`, `cah:RestorationEvent rdfs:subClassOf crm:E11_Modification`, and `cah:ProvenanceEvent rdfs:subClassOf crm:E10_Transfer_of_Custody`. Subclass extensions of EDM include `cah:Artwork rdfs:subClassOf edm:ProvidedCHO`. Subproperty alignments include `cah:createdBy` as the inverse of `crm:P14_carried_out_by`, `cah:heldBy` aligned to `crm:P50_has_current_keeper`, and `cah:locatedIn` aligned to `crm:P53_has_former_or_current_location`. Complex relational axioms were added in a second LLM-assisted pass, including cardinality constraints (many-to-many for Artist–Artwork), anti-symmetry (Artwork `createdInPeriod` ArtPeriod), and five inverse property pairs.

## Mappings

**Structured data mapping.** The `convert_json.py` script loads the department-grouped Met JSON and maps each object record to ABox triples using the rdflib Python library. The mapping logic in `helpers.py` creates typed instances (`cah:Artwork`, `cah:Artist`, `cah:Institution`, `cah:Medium`, `cah:Genre`, `cah:ArtPeriod`) and links them via properties such as `cah:createdBy`, `cah:heldBy`, `cah:usesMedium`, `cah:hasGenre`, `cah:createdInPeriod`, and `cah:hasCreationDate`. Artist names are normalised and hashed to produce stable URIs, and unknown artists are mapped to a dedicated `cah:artist_unknown` individual. The ontology TBox is optionally merged into the same output graph, producing the complete structured KG (`rdf/structured_kg.ttl`).

**Unstructured data mapping.** The pipeline consists of four sequential scripts: `fetch_unstructured.py` retrieves raw Wikipedia text; `clean_unstructured.py` removes citation markers, wiki formatting, and noise; `chunk_unstructured.py` splits sections into ≤500-character chunks with semantic labels; and `extract_unstructured.py` runs spaCy NER (`en_core_web_sm`) to extract entity–predicate–object triples. The `convert_to_turtle.py` script then maps extracted predicates to ontology properties (e.g., PERSON → `cah:createdBy`, GPE → `cah:locatedIn`, DATE → `cah:hasBirthDate`), applies noise filtering via blocklist/allowlist heuristics, and serialises the result as Turtle. Manually verified seed triples supplement critical facts that NER missed. The pipeline extracted 4,966 candidate triples, of which 2,584 survived noise filtering.

## Queries

Twenty SPARQL queries were written to answer all 20 competency questions (10 manual, 10 LLM-generated). The queries exercise a broad range of SPARQL features:

- **Basic graph pattern matching** (CQ7 — Louvre location; CQ10 — Michelangelo sculptures)
- **Multi-hop joins** across 3–4 entities (CQ1 — artist birthplace + period + artwork; CQ2 — movement + institution; CQ11 — artist + exhibition + museum + year; CQ13 — provenance chain; CQ15 — curator + exhibition + artwork + period; CQ20 — cross-movement influence)
- **Aggregation** with GROUP BY, HAVING, COUNT, MIN, MAX (CQ3, CQ5, CQ9, CQ12, CQ14, CQ16, CQ18, CQ19)
- **Temporal filtering** with FILTER and date comparisons (CQ1, CQ5, CQ8, CQ12, CQ16)
- **Negation** via FILTER NOT EXISTS (CQ17 — artworks never exhibited)
- **BIND construct** for century bucketing (CQ16 — medium distribution across eras)

Queries were executed against the populated KG. Of the 20, 16 returned non-empty results with the current instance data. The 4 that returned empty (CQ3, CQ12, CQ13, CQ15) are limited by instance coverage gaps (no RestorationEvent, ProvenanceEvent, or Curator instances) rather than query logic errors — these gaps are analysed in the Completion Analysis document.

## KG Completion and RAG Strategy

The completion analysis identifies 5 incomplete ontology elements (e.g., missing artwork subtypes, absent Technique and Gallery classes, no Continent class for transitive geographic reasoning) and 5 incomplete instance elements (e.g., zero Exhibition, RestorationEvent, and ProvenanceEvent instances). A RAG strategy is proposed: for each gap, a natural language query is formulated, relevant text is retrieved from Wikipedia, and an LLM generates valid Turtle triples conforming to the `cah:` schema. Generated triples are parsed with rdflib for syntactic validation and manually checked against domain/range constraints before merging into the final KG. Full details are provided in the separate Completion Analysis document.

## Evaluation Methodology

Evaluation follows two dimensions: **performance** and **quality**.

*Performance.* The automated pipeline (`kg_pipeline.py`) is timed at each stage — ontology generation, data ingestion, and SPARQL execution. Storage footprint is measured as the serialised Turtle file size. The system runs without specialised hardware; horizontal scaling (adding more data sources or departments) is straightforward, while vertical scaling (larger LLM models or richer NER) is possible but not required for this dataset size.

*Quality.* All 20 SPARQL queries were executed against the populated KG. Of these, 16 out of 20 returned non-empty, well-formed results. The 4 queries that returned empty results (CQ3, CQ12, CQ13, CQ15) do so because of instance coverage gaps — no RestorationEvent, ProvenanceEvent, or Curator instances exist in the current KG — rather than query logic errors. The competency questions themselves are not replaced; the unanswered ones are discussed as KG coverage limitations in the Completion Analysis. Compared to single-prompt LLM baselines, the KG provides more detailed, verifiable, and consistently reproducible answers.

## Limitations

The primary limitation is instance coverage. The Met Museum API does not expose exhibition, conservation, provenance, or curatorial data, which leaves several ontology classes unpopulated. The unstructured pipeline's reliance on spaCy `en_core_web_sm` introduces noise — the model misclassifies organisations as persons and locations as institutions in the cultural heritage domain, resulting in 2,382 out of 4,966 candidate triples being filtered. A fine-tuned BERT NER model would likely improve precision, but was not feasible due to dependency constraints (no Python 3.13 torch build on macOS at time of development). Additionally, Wikipedia articles exhibit selection bias toward Western European art, which skews the KG's coverage.

## Conclusion

This project demonstrates a reproducible, LLM-assisted pipeline for constructing a domain-specific knowledge graph from heterogeneous sources. The combination of structured API data (Met Museum) and unstructured text (Wikipedia) with ontology extensions of CIDOC-CRM and EDM produces a KG that answers the majority of the 20 competency questions via SPARQL. Key limitations — particularly the absence of exhibition, conservation, and provenance instances — are addressed through a proposed RAG completion strategy. The full codebase, ontology files, SPARQL queries, and documentation are publicly available in the project repository.
