# LLM Prompts Document — All Tasks

**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2
**Domain:** Arts and Cultural Heritage
**Team:** Vishal Thakwani, Oluwatamilore Oshinnaike, Jia Er Tee, Hristina Georgieva, Yusuf Rahman

This document consolidates all LLM prompts used across every knowledge engineering task in the project.

---

## 1. Competency Question Generation (Domain Expert — Vishal Thakwani)

**KE Task:** Augmenting the 10 manual competency questions with 10 LLM-generated ones (CQs 11–20).

A three-stage iterative prompting strategy was used:

### Prompt A — Domain Scoping and Ontology Alignment

> "Act as a knowledge engineer specialising in cultural heritage ontologies. Our group is building a knowledge graph for the Arts and Cultural Heritage domain, covering artworks (paintings, sculptures, prints, drawings, photographs, installations), artists, museums, galleries, exhibitions, conservation events, acquisition events, art periods and movements, mediums, techniques, genres, and awards. We are extending two existing ontologies: CIDOC-CRM (ISO 21127, the international standard for cultural heritage documentation) and the Europeana Data Model (EDM). The core classes include: Artwork (with subtypes Painting, Sculpture, Photograph, Print, Drawing, Installation), Person (Artist, Curator, Conservator, Collector), CulturalInstitution (Museum, Gallery), Place (City, Country, Continent), Event (Exhibition, ConservationEvent, AcquisitionEvent), ArtPeriod, ArtMovement, Medium, Technique, Genre, Award. Key relationships include: createdBy, heldBy, createdDuring, usedMedium, hasGenre, exhibitedIn, locatedIn (transitive), bornIn, activeIn, influencedBy, memberOf, wonAward, restoredArtwork, acquisitionOf. Propose 10 competency questions that this knowledge graph should answer. The questions must be complex enough to require multi-hop SPARQL queries (joining across at least 2–3 entities), and should include at least two questions using aggregation (COUNT, MAX, MIN), at least two involving temporal reasoning (date ranges, ordering), and at least one using negation or absence patterns. The domain is strictly visual arts — exclude music, theatre, dance, and performing arts."

**Rationale:** Names every class and relationship from the domain concept sketch; specifies CIDOC-CRM and EDM by name; mandates multi-hop complexity, aggregation, temporal, and negation patterns; excludes performing arts.

### Prompt B — Complementarity and Gap-Filling

> "The following themes are already covered by our 10 manually crafted competency questions: (1) artist nationality + creation period filtering, (2) art movement membership + institution holding, (3) conservation event counting, (4) award winners, (5) most common medium before a date, (6) living artist reasoning + geographic containment, (7) transitive geographic location lookup, (8) temporal artwork filtering + institution, (9) multi-genre artists, (10) specific artist + artwork subtype + institution. Generate 10 REPLACEMENT competency questions that DO NOT overlap with any of these 10 themes. Instead, focus on these gaps: cross-institution exhibition comparisons, provenance/ownership chains across countries, art movement temporal span analysis, curatorial decisions across periods, century-level medium distribution changes, negation patterns for unexhibited works, multi-artist collaborative creations, patron/donor networks across museums, and artist influence chains across movements. Each question should be phrased as a natural language question a museum researcher or cultural heritage professional would realistically ask."

**Rationale:** Summarises each manual CQ's theme; names specific gap areas identified from the ontology concept sketch; anchors in real-world use cases.

### Prompt C — SPARQL Feasibility Refinement

> "For each of the 10 questions you generated, verify that it can be answered with a SPARQL query over an RDF knowledge graph using only the classes and properties defined above. If a question requires free-text reasoning, subjective judgement, or data not representable in the ontology (e.g., 'most influential', 'most important'), rephrase it to use only structured relationships and quantifiable measures. For example, replace 'most influential artist' with 'artist with the most influencedBy relationships pointing to them'. Also ensure each question involves at least two different classes from the ontology."

**Rationale:** Forces operationalisation of every question via triple patterns, FILTER, GROUP BY, HAVING, NOT EXISTS; catches class coverage gaps; prevents impossible queries.

---

## 2. Ontology Creation (Modelling Experts — Jia Er Tee, Oluwatamilore Oshinnaike)

**KE Task:** Generating the base ontology structure from competency questions and domain analysis.

### Prompt 2a — Ontology Design from Competency Questions

> "You are an ontology engineer designing an OWL ontology for the Cultural and Arts Heritage domain, extending both the Europeana Data Model Ontology (edm) and CIDOC-CRM Ontology (crm). Analyse the following 20 competency questions, and identify any classes, properties, relationships, and inverse properties between concepts mentioned that will be needed to answer these questions. Make sure to: 1: Have each suggestion be in the format: class/property name, type, rdfs:comment. 2: Return a structured list separated by commas. 3: Use subclasses from edm: or crm: where possible. [20 CQs listed]"

**Rationale:** Ensures all ontology elements are derived systematically from the competency questions rather than ad-hoc modelling.

### Prompt 2b — Ontology TTL Generation

> "Build an ontology with classes, object properties, data properties, and axioms in RDF format for a Cultural and Arts Heritage domain using the text below. Reference the existing CIDOC-CRM (crm:) and Europeana Data Model (edm:) ontologies. Incorporate data properties, inverse Properties, and ensure the hierarchy is well-structured. Make sure to: 1: Include any other prefixes and ontologies required for these two ontologies (crm: and edm:) to function. 2: Use this IRI and prefix for the base ontology: @prefix cah: <http://example.org/culturalheritage#>. 3: Reuse the EDM and CRM ontology classes and properties for creating the hierarchy. 4: Ensure the file is in a turtle format (.ttl). 5: Add rdfs:label and rdfs:comment to each class and property. [Full text specification of all classes and properties]"

**Rationale:** Provides a fully specified text input so the LLM generates syntactically correct Turtle that conforms to the agreed class hierarchy and namespace conventions.

### Prompt 2c — Complex Relations Addition

> "You are a senior knowledge engineer who has just been assigned the task to add complex relationships to the properties in the knowledge graph supplied to you. You need to derive and add relational structures that demonstrate semantic patterns in the domain, include varied mapping cardinalities, and improve the underlying intelligence of the knowledge graph. Some examples you can reference are: Cardinality: Artist created Artwork has a many-to-many relationship, multiple artists can work on one artwork, and a singular artist can create multiple pieces of artworks. Binary Relation patterns: Artwork createdIn Art Period is an anti-symmetrical property, an art period cannot be createdIn an artwork. Please add all the necessary and sufficient complex relations to all the properties and give me the new ontology .ttl file. Please ensure you DO NOT change anything already included in the ontology, only add to it."

**Rationale:** Enriches the base ontology with cardinality constraints, symmetry/anti-symmetry axioms, and inverse property declarations without modifying existing definitions.

---

## 3. Unstructured Data Pipeline (Req./Data/LLM Pipeline — Hristina Georgieva)

**KE Task:** Designing the Wikipedia-based unstructured data extraction pipeline.

### Prompt 3a — Data Source Selection

> "Given the domain of Arts and Cultural Heritage, suggest 5 notable artists, 5 iconic artworks, and 3 major museums that would provide rich, structured information on Wikipedia for knowledge graph extraction. Focus on entities with well-documented Wikipedia pages covering biographical data, creation dates, locations, and institutional holdings."

### Prompt 3b — NER Entity-Predicate Mapping

> "Given a spaCy NER entity extracted from a Wikipedia article about an artist, artwork or museum, map the entity label to the most appropriate ontology predicate from the following list: createdBy, heldBy, locatedIn, influencedBy, hasGenre, participatedInExhibition, activeInMovement, wonPrize, usesMedium, hasBirthDate, hasCreationDate. Entity labels to map: PERSON, GPE, LOC, ORG, NORP, EVENT, DATE."

### Prompt 3c — Noise Filtering Design

> "Given that spaCy en_core_web_sm produces noisy entity extractions from Wikipedia text, what heuristic rules should be applied to filter out low-quality triples? Consider: possessives, generic words, numeric strings, very short entities, and wrong predicate-entity type combinations."

### Prompt 3d — Seed Triples Generation

> "Generate a set of verified RDF triples in Turtle format for the following entities using the cah: namespace (http://example.org/culturalheritage#): artists Leonardo da Vinci, Claude Monet, Frida Kahlo, Vincent van Gogh, Yayoi Kusama, Rembrandt, Pablo Picasso, Tracey Emin; artworks Mona Lisa, Water Lilies, The Night Watch, Guernica, My Bed; museums Louvre, Tate Modern, British Museum, Rijksmuseum, Museo Reina Sofia. Include hasBirthDate, locatedIn, createdBy, heldBy, and hasCreationDate triples mapped to the ontology."

### Prompt 3e — Ontology Mapping Verification

> "Given the following ontology properties: createdBy (domain: Artwork, range: Artist), heldBy (domain: Artwork, range: Institution), locatedIn (domain: Institution, range: Place), influencedBy (domain: Artist, range: Artist), hasBirthDate (domain: Artist, range: xsd:date), hasCreationDate (domain: Artwork, range: xsd:date) — verify that my predicate mappings are correct and identify any mismatches."

### Prompt 3f — Limitations Documentation

> "What are the main limitations of using spaCy en_core_web_sm for named entity recognition in the cultural heritage domain, compared to a fine-tuned BERT model? What would be the expected improvement in precision and recall?"

---

## 4. Structured Data Pipeline (Req./Data/LLM Pipeline — Yusuf Rahman)

**KE Task:** Mapping Met Museum JSON data to the ontology.

*(Yusuf's structured pipeline used programmatic mapping via rdflib rather than LLM prompts. The mapping logic is codified in `helpers.py` and `convert_json.py`. No LLM prompts were used for this pipeline step.)*

---

## 5. Automated KG Pipeline (Jia Er Tee)

**KE Task:** Orchestrating the end-to-end pipeline for ontology generation, data ingestion, RAG completion, and SPARQL execution.

Prompts 2b and 2c (from Section 2) are reused programmatically in the `kg_pipeline.py` script. The pipeline context differs from the manual workflow: the LLM receives the full text of the two existing OWL ontology files (CIDOC-CRM and EDM) as additional input alongside the prompt, and the output is parsed and saved automatically by the script rather than manually copied. The instruction text is identical, but the effective prompt (instruction + injected ontology context) is larger and produces results conditioned on the actual OWL definitions.

See Prompt 2b (pipeline_prompt_1) and Prompt 2c (pipeline_prompt_2) above for the full prompt text.

---

## Summary

| KE Task | Prompts Used | Team Member |
|---------|-------------|-------------|
| Competency Question Generation | 3 (A, B, C) | Vishal Thakwani |
| Ontology Design from CQs | 1 (2a) | Jia Er Tee, Tami Oshinnaike |
| Ontology TTL Generation | 1 (2b) | Jia Er Tee, Tami Oshinnaike |
| Complex Relations Addition | 1 (2c) | Jia Er Tee, Tami Oshinnaike |
| Unstructured Data Pipeline | 6 (3a–3f) | Hristina Georgieva |
| Structured Data Pipeline | 0 (programmatic) | Yusuf Rahman |
| Automated KG Pipeline | Reuses 2b + 2c with OWL context | Jia Er Tee |
| **Total** | **12 unique prompts** | |
