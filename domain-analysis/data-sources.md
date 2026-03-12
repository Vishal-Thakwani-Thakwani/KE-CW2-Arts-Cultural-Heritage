# Data Sources for Arts and Cultural Heritage Ontology

**Module:** 5CCSAKNE Knowledge Engineering — Coursework 2  
**Author:** Vishal Thakwani (Domain Expert)  
**Date:** 12 March 2026

---

## 1. Open APIs (No Authentication Required)

### Metropolitan Museum of Art (The Met)
- **URL:** https://metmuseum.github.io/
- **Format:** JSON REST API
- **Coverage:** 470,000+ artworks with high-resolution public domain images
- **Key fields:** title, artistDisplayName, objectDate, medium, department, culture, period, dynasty, classification, dimensions, country, city
- **Licence:** CC0 (public domain)
- **Why useful:** Massive dataset covering 5,000 years of art. Can populate Artwork, Artist, Medium, Period, and Place instances.

### Rijksmuseum
- **URL:** https://data.rijksmuseum.nl/
- **Format:** JSON API + Linked Data (RDF/Turtle)
- **Coverage:** 800,000+ objects, 320,000 bibliographic records, 70,000 thesaurus terms
- **Linked Data model:** Europeana Data Model + Linked Art
- **Licence:** CC0
- **Why useful:** Already uses CIDOC-CRM-aligned models. Can serve as a direct data source for our ontology population.

### Europeana
- **URL:** https://www.europeana.eu/en
- **Format:** REST API (JSON-LD)
- **Coverage:** 50+ million cultural heritage items from 3,000+ institutions across Europe
- **Licence:** Varies per item (CC0, CC-BY, etc.)
- **Why useful:** Aggregates metadata from thousands of GLAMs. Good for cross-institutional queries.

## 2. SPARQL Endpoints

### British Museum
- **Endpoint:** https://collection.britishmuseum.org/sparql
- **Model:** CIDOC-CRM
- **Coverage:** 2+ million objects
- **Why useful:** Uses CIDOC-CRM natively — excellent for validating our ontology alignment.

### Nomisma.org
- **Endpoint:** https://nomisma.org/sparql
- **Focus:** Numismatic heritage (coins, medals)
- **Model:** CIDOC-CRM extensions
- **Why useful:** Demonstrates domain-specific CIDOC-CRM extension patterns.

### Getty Vocabularies (LOD)
- **AAT:** http://vocab.getty.edu/aat/
- **ULAN:** http://vocab.getty.edu/ulan/
- **TGN:** http://vocab.getty.edu/tgn/
- **Format:** RDF/SPARQL
- **Why useful:** Standard reference vocabularies for art concepts, artist names, and geographic names.

## 3. Existing Ontologies to Reuse/Reference

| Ontology | URI | Description |
|----------|-----|-------------|
| CIDOC-CRM v7.1.3 | https://cidoc-crm.org/ | Core cultural heritage reference model (ISO 21127) |
| Europeana Data Model | https://pro.europeana.eu/page/edm-documentation | Metadata aggregation framework |
| Linked Art | https://linked.art/ | JSON-LD profile of CIDOC-CRM for art museums |
| Dublin Core | https://www.dublincore.org/specifications/dublin-core/ | Generic metadata standard |
| FOAF | http://xmlns.com/foaf/0.1/ | People and social connections |
| Schema.org | https://schema.org/ | General-purpose structured data vocabulary |

## 4. Recommended Sample Data for Ontology Population

For the coursework, I recommend populating the ontology with ~30-50 instances covering:

### Artists (10-15)
- Leonardo da Vinci, Michelangelo, Rembrandt, Monet, Van Gogh, Picasso, Frida Kahlo, Banksy, Yayoi Kusama, Damien Hirst, J.M.W. Turner, Tracey Emin, Grayson Perry

### Artworks (15-20)
- Mona Lisa, David (Michelangelo), The Night Watch, Water Lilies series, Starry Night, Guernica, Girl with a Pearl Earring, The Great Wave, The Physical Impossibility of Death in the Mind of Someone Living, My Bed

### Institutions (5-10)
- The Louvre, British Museum, Tate Modern, Metropolitan Museum of Art, Rijksmuseum, Uffizi Gallery, MoMA, National Gallery London, Guggenheim

### Art Periods / Movements (5-8)
- Renaissance (1400-1600), Baroque (1600-1750), Impressionism (1860-1900), Cubism (1907-1920s), Surrealism (1920s-1960s), Pop Art (1950s-1970s), Contemporary Art (1970-present)

### Media / Techniques (5-8)
- Oil on canvas, Marble, Bronze, Watercolour, Fresco, Mixed media, Photography, Installation

This gives enough variety to demonstrate all competency questions and defined classes.
