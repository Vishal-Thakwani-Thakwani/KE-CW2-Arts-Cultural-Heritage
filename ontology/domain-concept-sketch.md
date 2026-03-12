# Domain Concept Sketch — For Modelling Experts

**Author:** Vishal Thakwani (Domain Expert)  
**Date:** 12 March 2026

This document provides a high-level view of the domain concepts and relationships I've identified through domain research. **This is input for the modelling experts** — the final ontology design, OWL axioms, defined classes, and extensions of existing ontologies are the modelling team's responsibility.

---

## Suggested Core Concepts

```
Artwork
  ├─ Painting
  ├─ Sculpture
  ├─ Photograph
  ├─ Print
  ├─ Drawing
  └─ Installation

Person
  ├─ Artist
  ├─ Curator
  ├─ Conservator
  └─ Collector

CulturalInstitution
  ├─ Museum
  └─ Gallery

Place
  ├─ City
  ├─ Country
  └─ Continent

Event
  ├─ Exhibition
  ├─ ConservationEvent
  └─ AcquisitionEvent

ArtPeriod
  └─ ArtMovement

Medium
Technique
Genre
Award
ArtistGroup
```

## Suggested Relationships

| From | Relationship | To | Notes |
|------|--------------|----|-------|
| Artwork | createdBy | Artist | Core |
| Artwork | heldBy | CulturalInstitution | Inverse: holdsArtwork |
| Artwork | createdDuring | ArtPeriod | |
| Artwork | usedMedium | Medium | Can be multiple |
| Artwork | usedTechnique | Technique | |
| Artwork | hasGenre | Genre | Can be multiple |
| Artwork | exhibitedIn | Exhibition | |
| CulturalInstitution | locatedIn | Place | **Suggest transitive** |
| Person | bornIn | Place | Functional |
| Artist | activeIn | ArtPeriod | |
| Artist | influencedBy | Artist | |
| Artist | wonAward | Award | |
| Artist | memberOf | ArtistGroup | |
| Exhibition | hostedAt | CulturalInstitution | |
| ConservationEvent | restoredArtwork | Artwork | |
| AcquisitionEvent | acquisitionOf | Artwork | |

## Suggested Data Properties

| Property | On | Type | Notes |
|----------|----|------|-------|
| artworkTitle | Artwork | string | |
| creationYear | Artwork | integer | |
| dimensions | Artwork | string | |
| personName | Person | string | |
| birthYear | Person | integer | |
| deathYear | Person | integer | Absent for living |
| nationality | Person | string | |
| institutionName | CulturalInstitution | string | |
| foundedYear | CulturalInstitution | integer | |
| periodName | ArtPeriod | string | |
| periodStart / periodEnd | ArtPeriod | integer | |
| placeName | Place | string | |
| mediumName | Medium | string | |
| techniqueName | Technique | string | |
| genreName | Genre | string | |
| awardName | Award | string | |

## Ideas for Defined Classes (for modelling team to consider)

These are domain-driven suggestions. The modelling experts decide which to implement as OWL equivalentClass axioms:

1. **RenaissancePainting** — Painting created 1400–1600
2. **MultidisciplinaryArtist** — Artist who created both a Painting and a Sculpture
3. **LivingArtist** — Artist with birthYear but no deathYear
4. **RestoredMasterpiece** — Artwork pre-1800 with at least one ConservationEvent
5. **LondonMuseum** — Museum located in London (tests transitive locatedIn)

## Existing Ontologies to Consider Extending

The spec requires extending 2 existing ontologies with 2+ subclasses and 2+ subproperties each:

| Candidate | CIDOC-CRM Classes to Extend | Notes |
|-----------|----------------------------|-------|
| CIDOC-CRM | E22 Human-Made Object → our Artwork subclasses; E21 Person → our Artist/Curator etc. | ISO standard, very well documented |
| Europeana Data Model | edm:ProvidedCHO → our Artwork; edm:Agent → our Person subtypes | Used by 3k+ EU institutions |
| Dublin Core | dc:creator, dc:date, dc:subject → our subproperties | Simple, widely adopted |

## Sample Instances I Can Validate Against

As domain expert, I'll validate the final KG against these real-world examples:

**Artists:** Leonardo da Vinci, Michelangelo, Rembrandt, Monet, Van Gogh, Picasso, Frida Kahlo, Banksy, Yayoi Kusama, Damien Hirst, J.M.W. Turner, Tracey Emin, Grayson Perry

**Artworks:** Mona Lisa, David, The Night Watch, Water Lilies, Starry Night, Guernica, My Bed, The Physical Impossibility of Death...

**Institutions:** Louvre, British Museum, Tate Modern, Met, Rijksmuseum, Uffizi, MoMA, National Gallery London
