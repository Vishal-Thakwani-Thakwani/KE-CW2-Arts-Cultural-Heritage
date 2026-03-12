# Domain Expert Report: Arts and Cultural Heritage

**Author:** Vishal Thakwani (Domain Expert)  
**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2  
**Date:** 12 March 2026

---

## 1. Domain Overview

The **Arts and Cultural Heritage** domain encompasses the creation, preservation, exhibition, and scholarly study of artworks and cultural artefacts. It spans galleries, libraries, archives, and museums (collectively known as **GLAMs**) and covers a timeline from antiquity to contemporary art.

This domain is rich in structured relationships — artworks are created by artists during specific periods, using specific materials and techniques, housed in institutions, exhibited in shows, subject to conservation, and passed through chains of ownership (provenance). These characteristics make it an ideal candidate for ontological modelling.

## 2. Scope and Boundaries

For this coursework, the ontology focuses on:

- **Artworks** (paintings, sculptures, prints, drawings, photographs, installations)
- **Artists and creators** (individuals and groups)
- **Cultural institutions** (museums, galleries, archives)
- **Exhibitions** (temporary and permanent displays)
- **Conservation and restoration** events
- **Historical and art periods** (Renaissance, Baroque, Impressionism, etc.)
- **Materials and techniques** used in creation
- **Provenance** (ownership history)
- **Geographic locations** (where art was created, where it is held)
- **Awards and recognition** (Turner Prize, Venice Biennale, etc.)

**Out of scope:** performing arts (music, theatre, dance), digital-only NFTs, literary works.

## 3. Key Concepts (Classes)

The following core concepts form the backbone of the ontology:

### 3.1 Physical and Conceptual Objects
| Class | Description | CIDOC-CRM Mapping |
|-------|-------------|-------------------|
| `Artwork` | A physical or conceptual work of art | E22 Human-Made Object / E28 Conceptual Object |
| `Painting` | Subclass of Artwork — a painted work | E22 Human-Made Object |
| `Sculpture` | Subclass of Artwork — a three-dimensional work | E22 Human-Made Object |
| `Photograph` | Subclass of Artwork — a photographic work | E22 Human-Made Object |
| `Print` | Subclass of Artwork — a printed work (etching, lithograph) | E22 Human-Made Object |
| `Drawing` | Subclass of Artwork — a drawn work | E22 Human-Made Object |
| `Installation` | Subclass of Artwork — a site-specific or spatial work | E22 Human-Made Object |
| `Collection` | A curated group of artworks | E78 Curated Holding |

### 3.2 Actors
| Class | Description | CIDOC-CRM Mapping |
|-------|-------------|-------------------|
| `Person` | A human individual | E21 Person |
| `Artist` | A person who creates artworks (subclass of Person) | E21 Person (via P14 carried out by) |
| `Curator` | A person who organises exhibitions | E21 Person |
| `Conservator` | A person who preserves/restores artworks | E21 Person |
| `Collector` | A person who owns/collects artworks | E21 Person |
| `ArtistGroup` | A collective or movement of artists | E74 Group |

### 3.3 Institutions and Places
| Class | Description | CIDOC-CRM Mapping |
|-------|-------------|-------------------|
| `CulturalInstitution` | A museum, gallery, archive, or library | E40 Legal Body |
| `Museum` | Subclass — dedicated to collecting and exhibiting | E40 Legal Body |
| `Gallery` | Subclass — focused on art display/sales | E40 Legal Body |
| `Place` | A geographic location | E53 Place |
| `City` | Subclass of Place | E53 Place |
| `Country` | Subclass of Place | E53 Place |

### 3.4 Events
| Class | Description | CIDOC-CRM Mapping |
|-------|-------------|-------------------|
| `CreationEvent` | The act of creating an artwork | E12 Production |
| `Exhibition` | A public display of artworks | E7 Activity |
| `ConservationEvent` | Restoration or preservation work | E11 Modification |
| `AcquisitionEvent` | Transfer of ownership | E8 Acquisition |
| `AuctionSale` | Sale of artwork at auction | E96 Purchase |

### 3.5 Temporal and Classificatory
| Class | Description | CIDOC-CRM Mapping |
|-------|-------------|-------------------|
| `ArtPeriod` | A historical/stylistic era (Renaissance, etc.) | E4 Period |
| `ArtMovement` | A specific art movement (Cubism, Surrealism) | E4 Period |
| `Medium` | Material used (oil on canvas, bronze, marble) | E57 Material |
| `Technique` | Method of creation (fresco, etching, casting) | E55 Type |
| `Genre` | Subject category (portrait, landscape, still life) | E55 Type |
| `Award` | Recognition given (Turner Prize, etc.) | E55 Type |

## 4. Key Relationships (Object Properties)

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `createdBy` | Artwork | Artist | Links artwork to its creator |
| `createdDuring` | Artwork | ArtPeriod | The period in which the work was made |
| `usedMedium` | Artwork | Medium | Material(s) used |
| `usedTechnique` | Artwork | Technique | Technique(s) employed |
| `hasGenre` | Artwork | Genre | Subject genre classification |
| `heldBy` | Artwork | CulturalInstitution | Current holding institution |
| `locatedIn` | CulturalInstitution | Place | Where the institution is |
| `exhibitedIn` | Artwork | Exhibition | Exhibitions featuring the work |
| `organisedBy` | Exhibition | CulturalInstitution / Curator | Who organised the exhibition |
| `hostedAt` | Exhibition | CulturalInstitution | Venue of the exhibition |
| `restoredBy` | ConservationEvent | Conservator | Who performed conservation |
| `restoredArtwork` | ConservationEvent | Artwork | What was conserved |
| `bornIn` | Person | Place | Birthplace of a person |
| `activeIn` | Artist | ArtPeriod | Period(s) the artist was active |
| `memberOf` | Artist | ArtistGroup | Artist membership in a collective |
| `ownedBy` | Artwork | Person / CulturalInstitution | Provenance/current owner |
| `previousOwner` | AcquisitionEvent | Person / CulturalInstitution | Prior owner in chain |
| `wonAward` | Artist / Artwork | Award | Award received |
| `placeInCountry` | City | Country | City to country relationship |
| `influencedBy` | Artist | Artist / ArtMovement | Artistic influences |

## 5. Key Data Properties

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `artworkTitle` | Artwork | xsd:string | Title of the artwork |
| `creationYear` | Artwork | xsd:integer | Year of creation |
| `dimensions` | Artwork | xsd:string | Physical dimensions |
| `personName` | Person | xsd:string | Full name |
| `birthYear` | Person | xsd:integer | Year of birth |
| `deathYear` | Person | xsd:integer | Year of death |
| `nationality` | Person | xsd:string | Nationality |
| `exhibitionTitle` | Exhibition | xsd:string | Name of exhibition |
| `startDate` | Exhibition | xsd:date | Exhibition start |
| `endDate` | Exhibition | xsd:date | Exhibition end |
| `mediumName` | Medium | xsd:string | Name of material |
| `periodName` | ArtPeriod | xsd:string | Name of period |
| `periodStart` | ArtPeriod | xsd:integer | Start year of period |
| `periodEnd` | ArtPeriod | xsd:integer | End year of period |
| `institutionName` | CulturalInstitution | xsd:string | Name of institution |
| `foundedYear` | CulturalInstitution | xsd:integer | Year founded |
| `awardName` | Award | xsd:string | Name of the award |
| `awardYear` | Award | xsd:integer | Year awarded |

## 6. Proposed Defined Classes (OWL2)

These classes use equivalentClass axioms for automatic classification by a DL reasoner:

1. **`RenaissancePainting`** — A Painting whose creationYear falls between 1400 and 1600.
2. **`MultidisciplinaryArtist`** — An Artist who created both a Painting and a Sculpture.
3. **`InternationalExhibition`** — An Exhibition hosted at institutions in more than one Country.
4. **`RestoredMasterpiece`** — An Artwork that has been the subject of at least one ConservationEvent and was created before 1800.
5. **`LivingArtist`** — An Artist with a birthYear but no deathYear recorded.
6. **`ProvenancedArtwork`** — An Artwork involved in at least two AcquisitionEvents (rich ownership history).

## 7. Existing Ontologies and Standards

### 7.1 CIDOC-CRM (ISO 21127:2023)
The definitive standard for cultural heritage. Defines ~90 classes and ~160 properties. Our ontology should align with CIDOC-CRM where possible, though we create a simplified subset suitable for this coursework.

### 7.2 Europeana Data Model (EDM)
Used by Europeana.eu to aggregate metadata from 3,000+ European institutions. Provides classes like `edm:ProvidedCHO` (cultural heritage object) and properties for linking to providers.

### 7.3 Linked Art
A JSON-LD based profile of CIDOC-CRM used by the Getty, Yale, the Smithsonian, and others. Focuses on art museum use cases.

### 7.4 Getty Vocabularies
- **AAT** (Art & Architecture Thesaurus) — 400,000+ terms for art concepts
- **ULAN** (Union List of Artist Names) — 300,000+ artist records
- **TGN** (Thesaurus of Geographic Names) — 2,000,000+ place names

## 8. Alignment with CIDOC-CRM

The table in Section 3 shows how each proposed class maps to CIDOC-CRM. This alignment ensures our ontology is interoperable with international cultural heritage data while remaining simple enough for coursework scope.

## 9. Recommendations for the Team

1. **Modelling Experts:** Use Protégé with the HermiT reasoner. Define at least 5 equivalentClass axioms for the defined classes above. Use `owl:TransitiveProperty` for `locatedIn` (city → country → continent).
2. **Data Integration:** Pull sample data from the Metropolitan Museum API (free, no key needed) and the Rijksmuseum API. Map JSON fields to ontology properties.
3. **LLM Pipeline:** Use prompts to generate an alternative ontology from the competency questions, then compare with the manual version.
4. **Domain Validation:** I will validate the ontology against real-world examples from the British Museum, Tate, and Louvre collections.
