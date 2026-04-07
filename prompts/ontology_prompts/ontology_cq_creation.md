# Ontology Design from Competency Questions

### User Prompt (ChatGPT)

```
You are an ontology engineer designing an OWL ontology for the Cultural and Arts Heritage domain, extending both the Europeana Data Model Ontology (edm) and CIDOC-CRM Ontology (crm). Analyse the following 20 competency questions, and identify any classes, properties, relationships, and inverse properties between concepts mentioned that will be needed to answer these questions.

Make sure to:
1: Have each suggestion be in the format: class/property name, type, rdfs:comment
2: Return a structured list separated by commas.
3: Use subclasses from edm: or crm: where possible.

Below is an example competency question and answer, please follow the same format to answer all 20 competency questions:

CQ1: Which artists have won the Turner Prize?


Artist, owl:Class,  Some who creates art, such as painting or sculptures.
hasPrize, owl:ObjectProperty, Relates an artist to a prize that they have won. 
Prize, owl:Class, An award for an artists piece of work.

Competency Questions:
CQ1: Which artworks in the collection were created by artists born in Italy during the Renaissance period (1400–1600)?
CQ2: Which museums hold paintings by artists who were active in the Impressionist movement?
CQ3: Which artworks have been through more than one conservation/restoration event?
CQ4: Which artists have won the Turner Prize, and in which year?
CQ5: What is the most common medium used for artworks created before 1500?
CQ6: Which living artists have artworks held in museums located in London?
CQ7: In which country is the Musée du Louvre located?
CQ8: Which artworks were created before 1700 and are currently held by a museum?
CQ9: Which artists created works in more than one genre (e.g., both portraits and landscapes)?
CQ10: Which artworks by Michelangelo are classified as sculptures, and which institution holds them?
CQ11: Which artists have had artworks exhibited at more than one museum during the same calendar year, and which museums were involved?
CQ12: Which artworks have undergone more than two restoration events, and what is the time span between the earliest and most recent restoration?
CQ13: Which artworks have changed ownership across at least two different countries, and what was the sequence of provenance events with dates and acquiring institutions?
CQ14: For each art movement represented in the knowledge graph, what is the date range of artworks associated with it (earliest and latest creation year), and how many distinct artists contributed?
CQ15: Which curators have organised exhibitions featuring artworks from more than one art period, and which periods were combined in those exhibitions?
CQ16: How has the distribution of artistic mediums (oil on canvas, sculpture, photography, etc.) in museum collections changed across centuries (pre-1500, 1500–1700, 1700–1900, post-1900)?
CQ17: Which artworks in the knowledge graph have never been part of any exhibition, and which museums currently hold them?
CQ18: Which artworks were created collaboratively by more than one artist, and do those artists belong to the same art movement or different ones?
CQ19: Which collectors or donors have contributed artworks to more than one museum, and how many artworks did each donate in total across all institutions?
CQ20: Which artists influenced other artists who created works in a different art movement from their own?

Provide the answers in the format:
(Class/Property Name) , (Type) , (rdfs:comment)
```

### Model Response

```
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

## Justification 
To be continued...
