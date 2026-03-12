# Competency Questions for Arts and Cultural Heritage Ontology

**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2  
**Domain Expert:** Vishal Thakwani  
**Date:** 12 March 2026

These 20 competency questions define what the ontology must be able to answer. Each question is paired with a rationale explaining which ontology concepts it exercises.

---

## Required/Core Questions

### CQ1: Which artworks in the collection were created by artists born in Italy during the Renaissance period (1400–1600)?
**Rationale:** Tests `createdBy`, `bornIn`, `creationYear` filtering, and the relationship between Artist and Place.

### CQ2: Which museums hold paintings by artists who were active in the Impressionist movement?
**Rationale:** Tests `heldBy`, `createdBy`, `activeIn`/`memberOf` linking artists to ArtMovement, and the Painting subclass.

### CQ3: Which artworks have been through more than one conservation event?
**Rationale:** Tests `restoredArtwork` with COUNT and HAVING — exercises the ConservationEvent class.

### CQ4: Which artists have won the Turner Prize, and in which year?
**Rationale:** Tests `wonAward`, `awardName`, `awardYear` — validates Award modelling.

### CQ5: What is the most common medium used for artworks created before 1500?
**Rationale:** Tests `usedMedium` with GROUP BY and COUNT — aggregate query over Medium class.

---

## Extended Questions

### CQ6: Who created a particular artwork?
**Rationale:** Basic lookup via `createdBy` — validates core relationship.

### CQ7: Which institution currently holds a given artwork?
**Rationale:** Tests `heldBy` — validates provenance/current location.

### CQ8: What technique(s) were used to create a specific artwork?
**Rationale:** Tests `usedTechnique` — validates Technique class.

### CQ9: Which artworks belong to a particular genre (e.g., portrait, landscape)?
**Rationale:** Tests `hasGenre` — validates Genre classification.

### CQ10: Which exhibitions featured artworks from the Baroque period?
**Rationale:** Tests `exhibitedIn` combined with `createdDuring` and ArtPeriod — cross-class query.

### CQ11: Which artists are classified as MultidisciplinaryArtists (created both paintings and sculptures)?
**Rationale:** Tests the `MultidisciplinaryArtist` defined class — exercises OWL2 reasoning.

### CQ12: Which artworks qualify as RestoredMasterpieces (pre-1800 with conservation history)?
**Rationale:** Tests the `RestoredMasterpiece` defined class — exercises OWL2 reasoning.

### CQ13: Which paintings were created during the Renaissance?
**Rationale:** Tests the `RenaissancePainting` defined class — exercises OWL2 reasoning.

### CQ14: Which living artists have works held in museums in London?
**Rationale:** Tests `LivingArtist` defined class combined with `heldBy` and `locatedIn` — multi-hop query.

### CQ15: In which country is a given museum located?
**Rationale:** Tests `locatedIn` with transitivity (museum → city → country) — validates transitive property.

### CQ16: Which artworks were created before the year 1700?
**Rationale:** Simple FILTER on `creationYear` — validates date property.

### CQ17: How many artworks does each museum in the ontology hold?
**Rationale:** COUNT with GROUP BY on `heldBy` — aggregate institutional query.

### CQ18: Which artists influenced other artists in the dataset?
**Rationale:** Tests `influencedBy` — validates artist-to-artist relationships.

### CQ19: What is the nationality of Leonardo da Vinci?
**Rationale:** Simple property lookup — `nationality` data property.

### CQ20: Which artworks are classified as both Sculptures and belong to the Renaissance period?
**Rationale:** Tests intersection of subclass (Sculpture) with `createdDuring` (ArtPeriod) — validates cross-classification.

---

## Mapping to SPARQL Query Types

| Query Type | CQs |
|-----------|-----|
| Simple SELECT | CQ6, CQ7, CQ8, CQ9, CQ19 |
| FILTER (date/numeric) | CQ1, CQ5, CQ16, CQ20 |
| COUNT / GROUP BY / HAVING | CQ3, CQ5, CQ17 |
| Defined class (reasoner) | CQ11, CQ12, CQ13, CQ14 |
| Multi-hop / transitive | CQ2, CQ10, CQ14, CQ15 |
| ORDER BY / LIMIT | CQ4, CQ5 |
