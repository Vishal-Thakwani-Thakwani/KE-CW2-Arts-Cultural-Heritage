# Unstructured Data Pipeline — LLM Prompts & Methodology

## Overview
This document describes the prompts and methodology used to design the unstructured data pipeline for the Arts & Cultural Heritage knowledge graph.

## 1. Data Source Selection Prompt
Used to identify suitable Wikipedia sources for the 5 artists, 5 artworks and 3 museums in our domain.

**Prompt:**
"Given the domain of Arts and Cultural Heritage, suggest 5 notable artists, 5 iconic artworks, and 3 major museums that would provide rich, structured information on Wikipedia for knowledge graph extraction. Focus on entities with well-documented Wikipedia pages covering biographical data, creation dates, locations, and institutional holdings."

## 2. NER Entity-Predicate Mapping Prompt
Used to design the mapping between spaCy NER entity types and ontology predicates.

**Prompt:**
"Given a spaCy NER entity extracted from a Wikipedia article about an artist, artwork or museum, map the entity label to the most appropriate ontology predicate from the following list: createdBy, heldBy, locatedIn, influencedBy, hasGenre, participatedInExhibition, activeInMovement, wonPrize, usesMedium, hasBirthDate, hasCreationDate. Entity labels to map: PERSON, GPE, LOC, ORG, NORP, EVENT, DATE."

## 3. Noise Filtering Design Prompt
Used to design the blocklist and filtering rules for noisy NER extractions.

**Prompt:**
"Given that spaCy en_core_web_sm produces noisy entity extractions from Wikipedia text, what heuristic rules should be applied to filter out low-quality triples? Consider: possessives, generic words, numeric strings, very short entities, and wrong predicate-entity type combinations."

## 4. Seed Triples Design Prompt
Used to generate manually verified seed triples to supplement automated extraction.

**Prompt:**
"Generate a set of verified RDF triples in Turtle format for the following entities using the cah: namespace (http://example.org/culturalheritage#): artists Leonardo da Vinci, Claude Monet, Frida Kahlo, Vincent van Gogh, Yayoi Kusama, Rembrandt, Pablo Picasso, Tracey Emin; artworks Mona Lisa, Water Lilies, The Night Watch, Guernica, My Bed; museums Louvre, Tate Modern, British Museum, Rijksmuseum, Museo Reina Sofia. Include hasBirthDate, locatedIn, createdBy, heldBy, and hasCreationDate triples mapped to the ontology."

## 5. Ontology Mapping Prompt
Used to verify alignment between extracted predicates and the unified ontology.

**Prompt:**
"Given the following ontology properties: createdBy (domain: Artwork, range: Artist), heldBy (domain: Artwork, range: Institution), locatedIn (domain: Institution, range: Place), influencedBy (domain: Artist, range: Artist), hasBirthDate (domain: Artist, range: xsd:date), hasCreationDate (domain: Artwork, range: xsd:date) — verify that my predicate mappings are correct and identify any mismatches."

## 6. Known Limitations Documented via LLM Consultation

**Prompt used to document limitations:**
"What are the main limitations of using spaCy en_core_web_sm for named entity recognition in the cultural heritage domain, compared to a fine-tuned BERT model? What would be the expected improvement in precision and recall?"

**Key limitations identified:**
- spaCy en_core_web_sm misclassifies organisations as persons and locations as institutions
- BERT (dslim/bert-base-NER) was attempted but torch has no Python 3.13 build on macOS
- hasBirthDate is a FunctionalProperty but NER produces multiple dates per artist
- 2382 out of 4966 extracted triples were filtered as noisy
- Seed triples were added manually to supplement critical missing facts