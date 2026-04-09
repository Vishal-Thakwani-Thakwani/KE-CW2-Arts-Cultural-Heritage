# Meeting Minutes — Meeting 3

**Date:** 07/04/2026
**Platform:** Microsoft Teams
**Attendees:** Vishal Thakwani, Jia Tee, Oluwatamilore Oshinnaike, Yusuf Rahman, Hristina Georgieva
**Absent:** None

---

## Work Developed So Far

| Team Member | Role | Work Completed Since Last Meeting |
|---|---|---|
| Vishal Thakwani | Domain Expert | Still working on the report, as he needs additional information from each member of the group so it is most accurate |
| Jia Tee | Modelling Expert | Created base ontology extending CIDOC-CRM; Tami to import her ontology into Jia's to produce one unified ontology file |
| Oluwatamilore Oshinnaike | Modelling Expert | Working on extending a second ontology to be imported into the unified ontology |
| Yusuf Rahman | Req./Data/LLM Pipeline | Implemented structured data pipeline using SPARQL Anything to convert JSON data to RDF graph, later deciding to best use rdflib; awaiting final unified ontology to complete mapping |
| Hristina Georgieva | Req./Data/LLM Pipeline | Completed unstructured data pipeline (fetch, clean, chunk, extract scripts); extracted 7940 triples from Wikipedia articles using spaCy NER; awaiting final unified ontology |

---

## Discussion Points

1. Yusuf presented his structured pipeline approach — using SPARQL Anything to automatically convert JSON data to an RDF graph, later deciding to use rdflib. He noted that the pipeline is ready but mapping to the ontology cannot be finalised until the modelling team produces the single unified ontology file.
2. Jia clarified the ontology structure — two existing ontologies (CIDOC-CRM and a second one by Tami) are being imported into one curated ontology. Both pipeline members (Yusuf and Hristina) agreed this approach works and they just need the final file to complete their mappings.
3. Hristina volunteered to fill in the meeting minutes template and noted that Vishal's domain documentation was uploaded to a separate branch and needs to be merged into the main docs folder.
4. The team discussed meeting minutes format — whether to keep them on GitHub or as a separate Word document, agreeing to prepare both options.
5. The team agreed to hold an additional checkpoint meeting the following day to review progress and prepare for final submission.
6. Yusuf asked Vishal to review the coursework specification and research the RAG implementation requirements, since Vishal is currently available while the rest of the team is focused on pipeline and ontology work. This will give the pipeline team clarity on what to implement once the ontology mapping is complete.
7. Jia seconded this request, also asking Vishal to produce an organised checklist of all final deliverables to ensure nothing is missed before submission.

---

## Problems & Stoppers

| Problem | Impact | Strategy to Resolve |
|---|---|---|
| Pipeline team cannot finalise ontology mappings until unified ontology is complete | Blocks convert_to_turtle.py and final KG assembly | Modelling team to prioritise completing and pushing the unified ontology file as soon as possible |

---

## Action Items for Next Meeting (Checkpoint — 08/04/2026)

| Team Member | Task | Deadline |
|---|---|---|
| Vishal Thakwani | Review the coursework spec; research and document RAG implementation approach; produce organised deliverables checklist for the team | 08/04/2026 |
| Jia Tee | Complete and push unified ontology file so pipeline team can finalise mappings | 08/04/2026 |
| Oluwatamilore Oshinnaike | Finalise second ontology extension and merge into Jia's ontology | 08/04/2026 |
| Yusuf Rahman | Finalise structured data mapping to ontology once unified ontology is available | 08/04/2026 |
| Hristina Georgieva | Write convert_to_turtle.py; write prompts documentation; fill and submit meeting minutes | 08/04/2026 |

---

## Domain Expert Decisions Made

| Decision | Rationale |
|---|---|
| One unified ontology to be used by both pipeline members | Avoids mapping conflicts when merging structured and unstructured triples into the final KG |

---

**Minutes recorded by:** Hristina Georgieva