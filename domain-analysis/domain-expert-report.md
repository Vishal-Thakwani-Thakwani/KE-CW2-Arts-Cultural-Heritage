# Domain Expert Report: Arts and Cultural Heritage

**Author:** Vishal Thakwani (Domain Expert / Client)  
**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2  
**Date:** 12 March 2026

---

## 1. Domain Choice and Justification

We have chosen **Arts and Cultural Heritage** from the approved list. This domain is well-suited to this coursework because:

- **Rich existing ontologies:** CIDOC-CRM (ISO 21127:2023) is the international standard, plus Europeana Data Model, Linked Art, etc. — we need to extend at least 2 existing ontologies, and this domain has many to choose from.
- **Abundant data sources:** Both textual (Wikipedia articles, museum descriptions, exhibition reviews) and structured (Met Museum JSON API, Rijksmuseum API, British Museum SPARQL). The spec requires at least 1 of each.
- **Real-world relevance:** GLAMs (Galleries, Libraries, Archives, Museums) are actively building knowledge graphs. Our KG mirrors real industry practice.
- **Interesting competency questions:** The domain naturally supports varied query types (temporal, geographic, categorical, aggregation).

## 2. Project Objectives

As the domain expert, I am setting the following objectives for our KG:

1. **Represent artworks and their creators** — including metadata like medium, technique, dimensions, creation date
2. **Model cultural institutions** — museums and galleries, where they are located, what they hold
3. **Capture art historical context** — periods, movements, and their temporal boundaries
4. **Track conservation history** — restoration events on significant artworks
5. **Enable provenance reasoning** — ownership chains and acquisition events
6. **Support geographic reasoning** — transitive location relationships (city → country → continent)

## 3. Domain Scope and Boundaries

**In scope:**
- Visual arts: paintings, sculptures, prints, drawings, photographs, installations
- Artists and creators (individuals and groups)
- Cultural institutions (museums, galleries)
- Exhibitions
- Conservation/restoration events
- Art periods and movements
- Materials and techniques
- Provenance (ownership history)
- Geographic locations
- Awards and recognition

**Out of scope:**
- Performing arts (music, theatre, dance)
- Digital-only works / NFTs
- Literary works
- Detailed financial valuations

## 4. High-Level Domain Concepts

These are the key concepts I've identified from the domain that the **modelling experts** should consider when designing the ontology. This is not a prescriptive class hierarchy — the modelling team decides the final OWL structure.

### Core Entities
- **Artwork** — the central concept; subtypes include Painting, Sculpture, Photograph, Print, Drawing, Installation
- **Person** — human individuals; subtypes include Artist, Curator, Conservator, Collector
- **Cultural Institution** — subtypes include Museum, Gallery
- **Place** — subtypes include City, Country, Continent

### Events
- **Exhibition** — a public display of artworks at a venue
- **Conservation Event** — restoration or preservation work
- **Acquisition Event** — transfer of ownership

### Classificatory
- **Art Period / Movement** — Renaissance, Baroque, Impressionism, Cubism, etc.
- **Medium** — oil on canvas, marble, bronze, etc.
- **Technique** — fresco, etching, casting, etc.
- **Genre** — portrait, landscape, still life, historical, religious, abstract
- **Award** — Turner Prize, Venice Biennale Golden Lion, etc.

### Key Relationships to Consider
- Artwork → created by → Artist
- Artwork → held by → Institution
- Artwork → created during → Art Period
- Artwork → used medium/technique → Medium/Technique
- Institution → located in → Place (transitive: city → country → continent)
- Artwork → exhibited in → Exhibition
- Conservation Event → on artwork / by conservator
- Artist → born in → Place
- Artist → influenced by → Artist

## 5. Existing Ontologies to Extend

The spec requires extending **at least 2 existing ontologies** with 2+ subclasses and 2+ subproperties each. I recommend these candidates for the **modelling experts** to evaluate:

| Ontology | Why it fits | URL |
|----------|------------|-----|
| **CIDOC-CRM** (ISO 21127) | The international standard for cultural heritage documentation; ~90 classes, ~160 properties | https://cidoc-crm.org/ |
| **Europeana Data Model** | Used by 3,000+ European institutions; good for aggregating metadata | https://pro.europeana.eu/page/edm-documentation |
| **Linked Art** | JSON-LD profile of CIDOC-CRM used by Getty, Yale, Smithsonian | https://linked.art/ |
| **Dublin Core** | General metadata standard, widely used | https://www.dublincore.org/ |
| **FOAF** | People and social connections | http://xmlns.com/foaf/0.1/ |

The modelling team should pick 2 and define the extensions.

## 6. Domain Decisions Log

As domain expert, I'll maintain a running log of decisions made throughout the project:

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | Domain = Arts and Cultural Heritage | Rich ontologies, abundant data, real-world relevance | 06/03/2026 |
| 2 | Focus on visual arts only (not performing arts) | Keeps scope manageable for 5-person team | 12/03/2026 |
| 3 | Include conservation/provenance events | Enables interesting temporal queries and defined classes | 12/03/2026 |

## 7. Recommendations for Team

- **Modelling experts:** Evaluate CIDOC-CRM + one other ontology for extension. Consider `owl:TransitiveProperty` for geographic containment. Use Protégé with HermiT reasoner.
- **Pipeline team:** Start with the Met Museum API (free, no key, 470k+ artworks in JSON) as the structured source. For textual data, consider Wikipedia articles on major artworks/artists.
- **Everyone:** Document all LLM prompts used — this is worth 10 marks on its own.
