import json
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from urllib.parse import quote

# -----------------------------
# Configuration (paths relative to this script / repo layout)
# -----------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent

ONTOLOGY_FILE = _REPO_ROOT / "ontology" / "cultural_heritage_extended_kg.ttl"
JSON_FILE = _SCRIPT_DIR / "met_selected_by_department.json"
_RDF_DIR = _SCRIPT_DIR / "rdf"
OUTPUT_FILE = _RDF_DIR / "populated_cultural_heritage_kg.ttl"

BASE = "http://example.org/cultural#"
CH = Namespace(BASE)

# -----------------------------
# Helper Functions
# -----------------------------

def safe_uri(name):
  return URIRef(BASE + quote(str(name).replace(" ", "_")))

def add_if_not_exists(g, subject, predicate, obj):
  if (subject, predicate, obj) not in g:
    g.add((subject, predicate, obj))

# -----------------------------
# Load Ontology
# -----------------------------

g = Graph()
g.parse(str(ONTOLOGY_FILE), format="turtle")
g.bind("ch", CH)

# -----------------------------
# Load JSON Data
# -----------------------------

with JSON_FILE.open("r", encoding="utf-8") as f:
  data = json.load(f)

# -----------------------------
# Mapping Logic
# -----------------------------

for dept in data["departments"]:
  for obj in dept["objects"]:

    # ---------------------
    # Create Artwork
    # ---------------------
    artwork_uri = safe_uri(f"artwork_{obj['objectID']}")
    add_if_not_exists(g, artwork_uri, RDF.type, CH.Artwork)

    g.add((artwork_uri, RDFS.label, Literal(obj["title"])))
    g.add((artwork_uri, CH.objectURL, Literal(obj["objectURL"], datatype=XSD.anyURI)))

    # ---------------------
    # Medium
    # ---------------------
    if obj["medium"]:
      medium_uri = safe_uri(f"medium_{obj['medium']}")
      add_if_not_exists(g, medium_uri, RDF.type, CH.Medium)
      g.add((medium_uri, RDFS.label, Literal(obj["medium"])))
      g.add((artwork_uri, CH.hasMedium, medium_uri))

    # ---------------------
    # Artist Mapping
    # ---------------------
    if obj["constituents"]:
      for c in obj["constituents"]:
        artist_uri = safe_uri(f"artist_{c['constituentID']}")
        add_if_not_exists(g, artist_uri, RDF.type, CH.Artist)
        g.add((artist_uri, RDFS.label, Literal(c["name"])))

        g.add((artwork_uri, CH.createdBy, artist_uri))

    # ---------------------
    # TimeSpan + CreationEvent
    # ---------------------
    if obj["objectBeginDate"]:

      creation_event_uri = safe_uri(f"creation_{obj['objectID']}")
      timespan_uri = safe_uri(f"timespan_{obj['objectID']}")

      add_if_not_exists(g, creation_event_uri, RDF.type, CH.CreationEvent)
      add_if_not_exists(g, timespan_uri, RDF.type, CH.TimeSpan)

      g.add((creation_event_uri, CH.hasTimeSpan, timespan_uri))
      g.add((timespan_uri, CH.startDate,
              Literal(obj["objectBeginDate"], datatype=XSD.gYear)))

      if obj["objectEndDate"]:
        g.add((timespan_uri, CH.endDate,
                Literal(obj["objectEndDate"], datatype=XSD.gYear)))

      g.add((artwork_uri, CH.wasCreatedIn, creation_event_uri))

    # ---------------------
    # Period (if present)
    # ---------------------
    if obj["period"]:
      period_uri = safe_uri(f"period_{obj['period']}")
      add_if_not_exists(g, period_uri, RDF.type, CH.ArtPeriod)
      g.add((period_uri, RDFS.label, Literal(obj["period"])))
      g.add((artwork_uri, CH.createdInPeriod, period_uri))

    # ---------------------
    # Museum / Repository
    # ---------------------
    if obj["repository"]:
      museum_uri = safe_uri("met_museum")
      add_if_not_exists(g, museum_uri, RDF.type, CH.Museum)
      g.add((museum_uri, RDFS.label, Literal(obj["repository"])))
      g.add((artwork_uri, CH.heldBy, museum_uri))

    # ---------------------
    # Country / City
    # ---------------------
    if obj["country"]:
      country_uri = safe_uri(f"country_{obj['country']}")
      add_if_not_exists(g, country_uri, RDF.type, CH.Country)
      g.add((country_uri, RDFS.label, Literal(obj["country"])))

      if obj["city"]:
        city_uri = safe_uri(f"city_{obj['city']}")
        add_if_not_exists(g, city_uri, RDF.type, CH.City)
        g.add((city_uri, RDFS.label, Literal(obj["city"])))
        g.add((city_uri, CH.hasCountry, country_uri))
        g.add((artwork_uri, CH.locatedIn, city_uri))
      else:
        g.add((artwork_uri, CH.locatedIn, country_uri))

# -----------------------------
# Save Graph
# -----------------------------

_RDF_DIR.mkdir(parents=True, exist_ok=True)
g.serialize(destination=str(OUTPUT_FILE), format="turtle")

print(f"Knowledge graph populated successfully → {OUTPUT_FILE}")