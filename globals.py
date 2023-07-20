""" Global variables. """

# Software information
SOFTWARE_ACRONYM = "ontouml-json2graph"
SOFTWARE_NAME = "OntoUML JSON2Graph Decoder"
SOFTWARE_VERSION = "2023.07.20"
SOFTWARE_URL = "https://w3id.org/ontouml/json2graph"

# Formats for saving graphs supported by RDFLib
# https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html#saving-rdf
ALLOWED_GRAPH_FORMATS = ["turtle", "ttl", "turtle2", "xml", "pretty-xml", "json-ld", "ntriples", "nt", "nt11", "n3",
                         "trig", "trix", "nquads"]

# URIs
URI_ONTOUML = "https://w3id.org/ontouml#"

# ONTOUML ENUMERATIONS

ENUM_RELATION_STEREOTYPE = ["material", "derivation", "comparative", "mediation", "characterization",
                            "externalDependence", "componentOf", "memberOf", "subCollectionOf", "subQuantityOf",
                            "instantiation", "termination", "participational", "participation", "historicalDependence",
                            "creation", "manifestation", "brigsAbout", "triggers"]

ENUM_PROPERTY_STEREOTYPE = ["begin", "end"]

ENUM_ONTOLOGICAL_NATURE = ["abstract", "collective", "event", "extrinsic-mode", "functional-complex", "intrinsic-mode",
                           "quality", "quantity", "relator", "situation", "type"]

# GROUPS OF CONCEPTS

ELEMENT_VIEW_TYPES = ["ClassView", "PackageView", "GeneralizationSetView", "RelationView", "GeneralizationView",
                      "NoteView"]

MODEL_ELEMENTS = ["Class", "Property", "Generalization", "GeneralizationSet", "Relation", "Cardinality"]
