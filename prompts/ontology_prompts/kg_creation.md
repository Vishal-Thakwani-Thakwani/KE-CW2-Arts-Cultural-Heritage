# Ontology Design from Competency Questions

### User Prompt (ChatGPT)

```
Build an ontology with classes, object properties, data properties, and axioms in RDF format for a Cultural and Arts Heritage domain. Reference the existing CIDOC-CRM (crm:) and Europeana Data Model (edm:) ontologies. Incorporate data properties, Inverse Properties, and ensure the hierarchy is well-structured. Make sure 

Make sure to:
1: Include any other prefixes and ontologies required for these two ontologies (crm: and edm:) to function.
2: Use this IRI and prefix for the base ontology: @prefix cah: <http://example.org/culturalheritage#> .
3: Reuse the EDM and CRM ontology classes and properties for creating the hierarchy of the ontology referenced in the text.
4: The file is in a turtle format (.ttl)


Here is a brief example, please follow the same format:

@prefix cah: <http://example.org/culturalheritage#> .
@prefix edm: <http://www.europeana.eu/schemas/edm/> .
@prefix crm: <http://www.cidoc-crm.org/cidoc-crm/> . 
@prefix ore: <http://www.openarchives.org/ore/terms/> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .


cah:Artist a owl:Class ;
    rdfs:label "Artist" ;
    rdfs:comment "A person who creates artworks" ;
    rdfs:subClassOf crm:E21_Person .

Text:
Artist, owl:Class, A person who creates artworks (subclass of crm:E21_Person).
Artwork, owl:Class, A cultural or artistic work (subclass of edm:ProvidedCHO or crm:E22_Man-Made_Object).
Museum, owl:Class, An institution that holds or exhibits artworks (subclass of crm:E40_Legal_Body).
Painting, owl:Class, A type of artwork created using paint (subclass of Artwork).
Sculpture, owl:Class, A three-dimensional artwork (subclass of Artwork).
ArtMovement, owl:Class, A style or movement in art history (subclass of crm:E55_Type).
ArtPeriod, owl:Class, A historical period classification (subclass of crm:E4_Period).
Genre, owl:Class, A category of artistic composition (subclass of crm:E55_Type).
Medium, owl:Class, The material or technique used in an artwork (subclass of crm:E57_Material).
Exhibition, owl:Class, An event where artworks are displayed (subclass of crm:E7_Activity).
RestorationEvent, owl:Class, An event of conservation/restoration (subclass of crm:E11_Modification).
CreationEvent, owl:Class, The act of creating an artwork (subclass of crm:E12_Production).
BirthEvent, owl:Class, The birth of a person (subclass of crm:E67_Birth).
ProvenanceEvent, owl:Class, An ownership transfer event (subclass of crm:E10_Transfer_of_Custody).
DonationEvent, owl:Class, A transfer of ownership as a donation (subclass of ProvenanceEvent).
Collector, owl:Class, A person or entity collecting artworks (subclass of crm:E39_Actor).
Curator, owl:Class, A person organizing exhibitions (subclass of crm:E21_Person).
Institution, owl:Class, An organization such as a museum (subclass of crm:E40_Legal_Body).
Country, owl:Class, A geopolitical entity (subclass of crm:E53_Place).
City, owl:Class, A subdivision of a country (subclass of crm:E53_Place).
TimeSpan, owl:Class, A temporal extent (subclass of crm:E52_Time-Span).

createdBy, owl:ObjectProperty, Relates an artwork to the artist who created it (inverse of crm:P14_carried_out_by).
createdInPeriod, owl:ObjectProperty, Relates an artwork to an art period.
hasCreationDate, owl:DatatypeProperty, The date when an artwork was created.
hasBirthPlace, owl:ObjectProperty, Relates an artist to their place of birth (crm:P98_brought_into_life).
hasBirthDate, owl:DatatypeProperty, The birth date of an artist.
activeInMovement, owl:ObjectProperty, Relates an artist to an art movement.
belongsToMovement, owl:ObjectProperty, Relates an artwork to an art movement.
hasGenre, owl:ObjectProperty, Relates an artwork to a genre.
usesMedium, owl:ObjectProperty, Relates an artwork to the medium used.
heldBy, owl:ObjectProperty, Relates an artwork to the institution that holds it (crm:P50_has_current_keeper).
locatedIn, owl:ObjectProperty, Relates an institution to a place (crm:P53_has_former_or_current_location).
participatedInExhibition, owl:ObjectProperty, Relates an artwork to an exhibition.
organizedBy, owl:ObjectProperty, Relates an exhibition to a curator.
hasParticipant, owl:ObjectProperty, Relates an exhibition to participating artworks or artists.
underwentRestoration, owl:ObjectProperty, Relates an artwork to restoration events.
hasTimeSpan, owl:ObjectProperty, Relates an event to its time span (crm:P4_has_time-span).
startDate, owl:DatatypeProperty, The start date of a time span.
endDate, owl:DatatypeProperty, The end date of a time span.
hasOwner, owl:ObjectProperty, Relates an artwork to its owner.
transferredOwnershipTo, owl:ObjectProperty, Relates a provenance event to the new owner.
transferredOwnershipFrom, owl:ObjectProperty, Relates a provenance event to the previous owner.
hasCountry, owl:ObjectProperty, Relates a place to a country.
influencedBy, owl:ObjectProperty, Relates an artist to another artist who influenced them.
collaboratedWith, owl:ObjectProperty, Relates artists who collaborated on an artwork.
wonPrize, owl:ObjectProperty, Relates an artist to a prize received.
Prize, owl:Class, An award given for artistic achievement.
awardYear, owl:DatatypeProperty, The year a prize was awarded.
donatedBy, owl:ObjectProperty, Relates an artwork to the donor.
donatedTo, owl:ObjectProperty, Relates a donation event to a museum.
hasContributor, owl:ObjectProperty, Relates an artwork to multiple contributing artists.
isLiving, owl:DatatypeProperty, Indicates whether an artist is alive.

inverse_createdBy, owl:ObjectProperty, Inverse of createdBy (artist to artworks created).
inverse_heldBy, owl:ObjectProperty, Inverse of heldBy (institution to artworks held).
inverse_participatedInExhibition, owl:ObjectProperty, Inverse of participatedInExhibition.
inverse_underwentRestoration, owl:ObjectProperty, Inverse of underwentRestoration.
inverse_influencedBy, owl:ObjectProperty, Inverse of influencedBy (influenced).
```

### Model Response
Outputs the .ttl file for the knowledge graph.
(put the reference here)

## Justification 
To be continued...
