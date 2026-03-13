# Competency Questions — Arts & Cultural Heritage KG

**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2  
**Author:** Vishal Thakwani (Domain Expert)  
**Date:** 12 March 2026 (manual CQs) | 13 March 2026 (LLM-augmented CQs)

Per the coursework spec, the domain expert leads a discussion to produce **10 manual competency questions**. The knowledge engineers then augment this with **10 additional LLM-generated questions** (documenting the prompts used — see `prompts/llm-competency-questions-prompts.md`).

---

## Part A: Manual Competency Questions (Domain Expert — CQs 1–10)

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

## Part B: LLM-Augmented Competency Questions (CQs 11–20)

**Prompt documentation:** See [`prompts/llm-competency-questions-prompts.md`](../prompts/llm-competency-questions-prompts.md)  
**Generated:** 13 March 2026 using iterative prompting strategy (3 prompts, documented with rationale)

These 10 questions were generated via LLMs and designed to **complement** the manual CQs by targeting more complex query patterns: multi-hop reasoning, temporal comparisons, aggregation, negation, and cross-entity inference.

### CQ11: Which artists have had artworks exhibited at more than one museum during the same calendar year, and which museums were involved?
**Type:** Multi-hop (Artist → Artwork → Exhibition → Museum) + temporal overlap + aggregation  
**Gap filled:** Cross-institution exhibition analysis — not covered by any manual CQ.

### CQ12: Which artworks have undergone more than two restoration events, and what is the time span between the earliest and most recent restoration?
**Type:** Aggregation (COUNT > 2) + temporal arithmetic (MAX date − MIN date)  
**Gap filled:** CQ3 checks for >1 restoration, but this goes deeper with temporal span analysis.

### CQ13: Which artworks have changed ownership across at least two different countries, and what was the sequence of provenance events with dates and acquiring institutions?
**Type:** Multi-hop (Artwork → AcquisitionEvent → Institution → Country) + ordering + counting  
**Gap filled:** Provenance and cross-border ownership chains — entirely absent from manual CQs.

### CQ14: For each art movement represented in the knowledge graph, what is the date range of artworks associated with it (earliest and latest creation year), and how many distinct artists contributed?
**Type:** Aggregation (MIN/MAX creation year, COUNT DISTINCT artists) grouped by ArtMovement  
**Gap filled:** Temporal span analysis of art movements — manual CQs reference movements only as filters.

### CQ15: Which curators have organised exhibitions featuring artworks from more than one art period, and which periods were combined in those exhibitions?
**Type:** Multi-hop (Curator → Exhibition → Artwork → ArtPeriod) + aggregation (COUNT DISTINCT periods > 1)  
**Gap filled:** Curatorial decision-making patterns — Curator class is not exercised by any manual CQ.

### CQ16: How has the distribution of artistic mediums (oil on canvas, sculpture, photography, etc.) in museum collections changed across centuries (pre-1500, 1500–1700, 1700–1900, post-1900)?
**Type:** Aggregation (COUNT per medium per century bucket) via FILTER  
**Gap filled:** CQ5 looks at the single most common medium before 1500; this analyses the full temporal distribution.

### CQ17: Which artworks in the knowledge graph have never been part of any exhibition, and which museums currently hold them?
**Type:** Negation (NOT EXISTS exhibition) + positive lookup (Artwork → heldBy → Museum)  
**Gap filled:** Negation/absence pattern — none of the manual CQs use NOT EXISTS.

### CQ18: Which artworks were created collaboratively by more than one artist, and do those artists belong to the same art movement or different ones?
**Type:** Aggregation (COUNT DISTINCT artists per artwork > 1) + comparison (same vs. different ArtMovement)  
**Gap filled:** Multi-artist collaborative works — manual CQs treat each artwork as single-creator.

### CQ19: Which collectors or donors have contributed artworks to more than one museum, and how many artworks did each donate in total across all institutions?
**Type:** Multi-hop (Collector → AcquisitionEvent → Artwork → Museum) + aggregation (COUNT artworks, COUNT DISTINCT museums > 1)  
**Gap filled:** Patron/donor network analysis — Collector role not exercised by any manual CQ.

### CQ20: Which artists influenced other artists who created works in a different art movement from their own?
**Type:** Multi-hop (Artist A → influencedBy → Artist B) + comparison (A.activeIn ≠ B.activeIn)  
**Gap filled:** Cross-movement influence chains — the influencedBy relationship is in the concept sketch but not tested by any manual CQ.

---

## Coverage Summary

| Aspect | Manual CQs (1–10) | LLM CQs (11–20) |
|---|---|---|
| Query depth | 1–2 hop lookups | 3–4 hop traversals |
| Temporal reasoning | Basic date filters | Date arithmetic, period spans, century bucketing |
| Aggregation | Simple COUNT, GROUP BY | COUNT with HAVING, MIN/MAX, multi-dimensional GROUP BY |
| Negation | Not covered | CQ17 (NOT EXISTS) |
| Provenance | Not covered | CQ13 (cross-border ownership) |
| Curation | Not covered | CQ15 (curatorial cross-referencing) |
| Artist influence | Not covered | CQ20 (cross-movement influence) |
| Collaboration | Not covered | CQ18 (multi-artist works) |
| Patronage | Not covered | CQ19 (donor network) |
| Cross-institution | Not covered | CQ11 (simultaneous exhibitions) |
