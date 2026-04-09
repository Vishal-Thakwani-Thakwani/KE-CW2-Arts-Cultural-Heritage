# Knowledge Graph Completion Analysis

**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2
**Domain:** Arts and Cultural Heritage
**Author:** Vishal Thakwani (Domain Expert)

---

## Overview

This document identifies 5 incomplete ontology elements and 5 incomplete instance elements in the current knowledge graph, and outlines a Retrieval-Augmented Generation (RAG) strategy to resolve them.

---

## Part A: Incomplete Ontology Elements (5)

### 1. Missing subclasses of Artwork

The domain-expert report specifies six artwork subtypes: Painting, Sculpture, Photograph, Print, Drawing, and Installation. The current ontology only defines `cah:Painting` and `cah:Sculpture` as subclasses of `cah:Artwork`. The remaining four subtypes — `cah:Photograph`, `cah:Print`, `cah:Drawing`, and `cah:Installation` — are absent, which means artworks of these types cannot be distinguished from the generic `cah:Artwork` class.

**Impact:** CQ10 asks specifically about sculptures; analogous queries filtering by photograph or print type would fail.

### 2. Missing Technique class

The domain concept sketch lists both Medium and Technique as separate concepts. The ontology defines `cah:Medium rdfs:subClassOf crm:E57_Material` but lacks a distinct `cah:Technique` class. Techniques such as fresco, etching, and casting are conflated with materials, losing an important semantic distinction.

**Impact:** Queries asking "which artworks were created using the etching technique?" cannot distinguish technique from medium.

### 3. Missing Gallery subclass of CulturalInstitution

The domain scope includes both museums and galleries as cultural institutions. While `cah:Museum rdfs:subClassOf crm:E40_Legal_Body` exists, there is no `cah:Gallery` class. Galleries that are not museums (e.g., commercial galleries, private galleries) cannot be accurately typed.

**Impact:** Queries asking "which galleries hold contemporary art?" would require matching on `cah:Museum`, which is semantically incorrect for non-museum galleries.

### 4. Missing Continent class and transitive locatedIn chain

The domain-expert report specifies transitive geographic reasoning (City → Country → Continent). The ontology has `cah:City` and `cah:Country` as subclasses of `crm:E53_Place`, but `cah:Continent` is absent. Additionally, `cah:locatedIn` is not declared as `owl:TransitiveProperty`, so reasoners cannot infer that an artwork held by a museum in Paris is also located in France and in Europe.

**Impact:** CQ6 requires geographic containment reasoning (museums in London → UK). Without transitivity and Continent, multi-hop geographic queries are incomplete.

### 5. Missing Conservator class

The domain-expert report lists Conservator as a subtype of Person alongside Artist, Curator, and Collector. The ontology defines `cah:Artist`, `cah:Curator`, and `cah:Collector` but has no `cah:Conservator` class. RestorationEvent uses `cah:underwentRestoration` to link artworks to events, but there is no way to type the person who performed the restoration.

**Impact:** Queries such as "which conservators have restored artworks at the British Museum?" cannot be expressed, and the RestorationEvent class lacks a complete set of participants even once instances are populated.

---

## Part B: Incomplete Instance Elements (5)

### 1. No Exhibition instances

The ontology defines `cah:Exhibition rdfs:subClassOf crm:E7_Activity` with properties `organizedBy` and `hasParticipant`, but the populated KG contains zero Exhibition instances. Neither the structured pipeline (Met API does not include exhibition data) nor the unstructured pipeline extracted exhibition triples.

**Impact:** CQ11, CQ15, and CQ17 (which uses NOT EXISTS on exhibitions) all depend on Exhibition instances.

### 2. No RestorationEvent instances

`cah:RestorationEvent rdfs:subClassOf crm:E11_Modification` is defined but unpopulated. The Met API does not include conservation data, and the Wikipedia pipeline did not extract restoration events.

**Impact:** CQ3 and CQ12 query restoration event counts and temporal spans; both return empty results.

### 3. No ProvenanceEvent or DonationEvent instances

The ontology models ownership transfer (`cah:ProvenanceEvent`) and donations (`cah:DonationEvent`) with properties like `transferredOwnershipTo/From` and `donatedBy/donatedTo`. No instances exist because neither data source provides provenance chain data.

**Impact:** CQ13 (cross-border ownership chains) and CQ19 (donor networks) cannot be answered.

### 4. No Curator or Collector instances

`cah:Curator` and `cah:Collector` are defined as subclasses of `crm:E21_Person` and `crm:E39_Actor` respectively, but no individuals of these types exist in the KG. The Met API only exposes artist names, not curators or collectors.

**Impact:** CQ15 (curators organising cross-period exhibitions) and CQ19 (collector donation patterns) return no results.

### 5. Missing ArtMovement and influence instances

While the ontology defines `cah:ArtMovement`, `cah:activeInMovement`, `cah:belongsToMovement`, and `cah:influencedBy`, the structured pipeline does not populate movement or influence data (the Met API lacks these fields). The unstructured pipeline extracts fewer than 10 movement-related triples (e.g., Impressionism, Surrealism, Cubism via NORP entities), providing minimal coverage.

**Impact:** CQ2 (Impressionist paintings), CQ14 (movement date ranges), CQ18 (collaborative works across movements), and CQ20 (cross-movement influence chains) are under-served.

---

## Part C: RAG Strategy for Completion

### Approach

A Retrieval-Augmented Generation (RAG) pipeline is used to resolve the identified gaps. The strategy combines the existing knowledge graph with external knowledge retrieved at query time, using an LLM to generate the missing triples.

### Pipeline

1. **Identify missing elements.** For each of the 10 gaps above, formulate a natural language query describing what information is needed (e.g., "What exhibitions has the Mona Lisa been displayed in?").

2. **Retrieve context.** Use the existing KG triples as grounding context, supplemented by targeted retrieval from Wikipedia or other authoritative sources. The retrieval step fetches relevant text passages that contain the missing information.

3. **Generate triples.** Prompt an LLM (GPT-5.3) with the retrieved context and the ontology schema, instructing it to output valid Turtle triples using the `cah:` namespace. The prompt includes the class/property definitions so the LLM produces correctly typed triples.

4. **Validate and merge.** Parse the generated Turtle with rdflib to check syntactic validity. Manually validate triples against the ontology's domain/range constraints. Merge validated triples into the final KG.

5. **Re-evaluate.** Re-run the 20 SPARQL queries against the augmented KG and measure improvement in query answerability.

### Implementation Status

The RAG strategy is outlined here as a designed approach. The pipeline infrastructure (LLM API calls, rdflib parsing, graph merging) exists in `kg_pipeline.py`, but full end-to-end execution across all 10 gaps was not completed before the submission deadline. The strategy has been validated on a subset of gaps (e.g., generating seed triples for artists and museums in the unstructured pipeline), demonstrating feasibility.

### Expected Outcome

With full execution, the RAG pipeline would populate Exhibition, RestorationEvent, ProvenanceEvent, Curator, Conservator, and Collector instances, and enrich ArtMovement and influence relationships, increasing CQ answerability from 16/20 to near-complete coverage.
