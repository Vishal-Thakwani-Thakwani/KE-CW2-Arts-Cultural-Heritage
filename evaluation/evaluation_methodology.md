# Performance evaluation

### Time (minutes)
```
How long does it take for the system to build the ontology/ run the pipeline (break it down to stages)?
In total the program takes X minutes to build the entire ontology.
Step 1. LLM-generated base ontology + complex relations takes X minutes.
Step 2. Data ingestion takes X minutes.
Step 3. RAG for missing elements takes X minutes. 
How long does it take for the system to answer all the SPARQL queries?
It takes X minutes to run all the sparql queries. 
```
### Memory (MegaBytes)
```
How much storage space does the ontology use up?
```
### Scalability (Likert Scale)
```
How scalable is this system? 
In terms of scalability, the system runs fairly well without extensive hardware, so although vertical scaling is possible it is not necessary. If more instances are needed and added, then horizontal scaling is the best choice and easily applicable.
```
# Quality Evaluation

### The KG answers the CQs well (Likert Scale) 
```
Are the answers the KG provides for the CQs factually correct and descriptive?
All 20 SPARQL queries were executed against the populated KG. Of these, 16 out of 20 returned non-empty, well-formed results. The 4 queries that returned empty results (CQ3, CQ12, CQ13, CQ15) do so because of instance coverage gaps — no RestorationEvent, ProvenanceEvent, or Curator instances exist in the current KG — rather than query logic errors. The competency questions themselves are not replaced; the unanswered ones are discussed as KG coverage limitations in the Completion Analysis. 
```
### The KG answers are better quality compared to simple prompts against an LLM (Likert Scale)
```
```
