# Competency Questions (Manual) — Domain Expert

**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2  
**Author:** Vishal Thakwani (Domain Expert)  
**Date:** 12 March 2026

Per the coursework spec, the domain expert leads a discussion to produce **10 manual competency questions**. The knowledge engineers will then augment this with **10 additional LLM-generated questions** (documenting the prompts used).

Below are the 10 manual competency questions I'm proposing for discussion at our next meeting.

---

## Manual Competency Questions (Domain Expert — 10)

### CQ1: Which artworks in the collection were created by artists born in Italy during the Renaissance period (1400–1600)?
**Rationale:** Tests creator-artwork-place-period chain. Requires joining Artist birthplace with artwork creation period.

### CQ2: Which museums hold paintings by artists who were active in the Impressionist movement?
**Rationale:** Multi-hop query across artwork type, holding institution, artist, and art movement.

### CQ3: Which artworks have been through more than one conservation/restoration event?
**Rationale:** Exercises event modelling with COUNT/HAVING aggregation.

### CQ4: Which artists have won the Turner Prize, and in which year?
**Rationale:** Validates the award/recognition modelling.

### CQ5: What is the most common medium used for artworks created before 1500?
**Rationale:** Aggregate query with GROUP BY/COUNT over materials and temporal filter.

### CQ6: Which living artists have artworks held in museums located in London?
**Rationale:** Requires reasoning about "living" (birth year exists, no death year), geographic containment (museum → city → country), and the artwork-institution relationship.

### CQ7: In which country is the Musée du Louvre located?
**Rationale:** Tests transitive geographic reasoning (Louvre → Paris → France).

### CQ8: Which artworks were created before 1700 and are currently held by a museum?
**Rationale:** Combines temporal filtering with institutional holding.

### CQ9: Which artists created works in more than one genre (e.g., both portraits and landscapes)?
**Rationale:** Tests the genre classification system with a cross-genre aggregation query.

### CQ10: Which artworks by Michelangelo are classified as sculptures, and which institution holds them?
**Rationale:** Tests artwork subtype classification with a specific artist filter and institution lookup.

---

## LLM-Generated Competency Questions (To Be Added)

The knowledge engineers will generate 10 additional CQs using LLM prompts. Requirements:
- Must be relevant to the Arts and Cultural Heritage domain
- Must complement (not duplicate) the 10 manual CQs above
- All prompts must be documented in `prompts/`

*This section will be filled in by the team.*
