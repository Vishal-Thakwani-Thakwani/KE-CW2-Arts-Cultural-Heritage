# Data Source Recommendations — Domain Expert

**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2  
**Author:** Vishal Thakwani (Domain Expert)  
**Date:** 12 March 2026

The coursework requires **at least 1 textual data source** and **at least 1 structured data source**. Below are my recommendations from a domain perspective. The **pipeline team** will evaluate feasibility and build the extraction/processing code.

---

## Structured Data Sources (JSON/XML/SQL/API)

### Metropolitan Museum of Art (The Met) — RECOMMENDED
- **URL:** https://metmuseum.github.io/
- **Format:** JSON REST API
- **Coverage:** 470,000+ artworks
- **Auth:** None required
- **Key fields:** title, artistDisplayName, objectDate, medium, department, culture, period, classification, dimensions, country, city
- **Licence:** CC0 (public domain)
- **Domain relevance:** Covers 5,000 years of art. Ideal for populating Artwork, Artist, Medium, Period, and Place instances.

### Rijksmuseum
- **URL:** https://data.rijksmuseum.nl/
- **Format:** JSON API + Linked Data (RDF/Turtle)
- **Coverage:** 800,000+ objects
- **Auth:** API key (free)
- **Licence:** CC0
- **Domain relevance:** Already uses CIDOC-CRM-aligned models. Good alternative or complement to Met.

### Europeana
- **URL:** https://www.europeana.eu/en
- **Format:** REST API (JSON-LD)
- **Coverage:** 50+ million items from 3,000+ institutions
- **Domain relevance:** Cross-institutional metadata. Good for breadth.

## Textual Data Sources

### Wikipedia Articles on Major Artworks/Artists — RECOMMENDED
- **Access:** Wikipedia API or scraped HTML
- **Format:** Unstructured text
- **Domain relevance:** Rich biographical, historical, and provenance information. Good for NLP/information extraction pipeline.

### Museum Exhibition Descriptions
- **Sources:** Tate, British Museum, National Gallery websites
- **Format:** HTML text
- **Domain relevance:** Exhibition metadata, artwork descriptions, curatorial notes.

### Art News / Reviews
- **Sources:** The Art Newspaper, Artnet News
- **Format:** Unstructured text
- **Domain relevance:** Current events, awards, exhibitions. Could feed into "Current news" aspect.

## SPARQL Endpoints (Existing KGs)

These can be accessed via API for data integration:

| Endpoint | Model | URL |
|----------|-------|-----|
| British Museum | CIDOC-CRM | https://collection.britishmuseum.org/sparql |
| Getty AAT | Custom | http://vocab.getty.edu/aat/ |
| Getty ULAN | Custom | http://vocab.getty.edu/ulan/ |
| Nomisma.org | CIDOC-CRM ext. | https://nomisma.org/sparql |

## Recommendation

For minimum viable effort, I recommend:
1. **Structured:** Met Museum JSON API (free, no auth, massive coverage)
2. **Textual:** Wikipedia articles on our sample artworks/artists

The pipeline team should confirm these work for their extraction approach.
