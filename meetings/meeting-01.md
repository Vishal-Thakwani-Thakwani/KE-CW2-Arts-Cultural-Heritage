# Meeting Minutes — Meeting 1

**Date:** 19/03/2026
**Platform:** Microsoft Teams
**Attendees:** Vishal Thakwani, Jia Tee, Oluwatamilore Oshinnaike, Yusuf Rahman, Hristina Georgieva
**Absent:** None

---

## Work Developed So Far

| Team Member | Role | Work Completed Since Last Meeting |
|---|---|---|
| Vishal Thakwani | Domain Expert | Set up GitHub repo, wrote domain expert report, 10 manual competency questions, 10 LLM-generated CQs with prompt documentation, data source recommendations, domain concept sketch |
| Jia Tee | Modelling Expert | Began reviewing existing ontologies and knowledge graphs for potential extension |
| Oluwatamilore Oshinnaike | Modelling Expert | Began reviewing existing ontologies and knowledge graphs for potential extension |
| Yusuf Rahman | Req./Data/LLM Pipeline | Initial research into data sources and pipeline tools |
| Hristina Georgieva | Req./Data/LLM Pipeline | Initial research into data sources and pipeline tools |

---

## Discussion Points

1. Git repository management — Agreed to create a dev branch as the main working branch. Each person/sub-team gets their own feature branch from dev. Tami and Yusuf assigned as reviewers for all merges into dev (two-person review system for quality control).
2. Modelling experts progress — Found existing ontologies and knowledge graphs for evaluation. Identified potential mapping sources from Wikipedia, museum APIs, OpenLink, and Schema.org. Currently reviewing 5 candidate sources and need to select the most relevant ones based on the 20 competency questions.
3. Development workflow — Recommended Google Colab or Jupyter Notebooks for quick code experimentation. Finalised code to be pushed to separate GitHub branches after testing. Separate branches needed for structured data processing vs. unstructured text processing.
4. Data cleaning — Pipeline team to begin data cleaning. Target was end of day / next day (20 March), but this is still in progress.

---

## Problems & Stoppers

| Problem | Impact | Strategy to Resolve |
|---|---|---|
| Ontology selection not yet finalised | Blocks detailed modelling work | Modelling experts to complete review by weekend (21–22 March) |
| Data cleaning not yet started | Delays pipeline development | Pipeline team to prioritise and provide timeline update |

---

## Action Items for Next Meeting

| Team Member | Task | Deadline |
|---|---|---|
| Vishal Thakwani | Set up GitHub branch structure and distribute meeting minutes | 21/03/2026 |
| Jia Tee | Finalise selection of 2 existing ontologies to extend (from CIDOC-CRM, Europeana, Schema.org, Dublin Core, FOAF, Linked Art) | 21/03/2026 |
| Oluwatamilore Oshinnaike | Support ontology selection and begin modelling work | 21/03/2026 |
| Yusuf Rahman | Begin structured and unstructured data preparation and cleaning | 21/03/2026 |
| Hristina Georgieva | Begin structured and unstructured data preparation and cleaning | 21/03/2026 |
| Everyone | Document all LLM prompts used (worth 10 marks in CW2 marking); Tuesday afternoon WhatsApp check-in call (5–10 min) | 21/03/2026 |

---

## Domain Expert Decisions Made

| Decision | Rationale |
|---|---|
| Visual arts scope confirmed (no performing arts) | Keeps KG focused and manageable for team of 5; aligns with data sources (Met Museum API, Rijksmuseum, British Museum) |
| Two-person review system for GitHub merges | Ensures quality control on ontology consistency and pipeline code before integration |
| Separate branches for structured vs. unstructured pipeline | CW2 requires at least 1 textual + 1 structured source; keeping them separate avoids merge conflicts and allows parallel work |

---

**Minutes recorded by:** Vishal Thakwani (Domain Expert)