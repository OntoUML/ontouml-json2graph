""" Global variables. """

# Software information
SOFTWARE_ACRONYM = "ontouml-json2graph"
SOFTWARE_NAME = "OntoUML JSON2Graph Decoder"
SOFTWARE_VERSION = "2023.06.15"
SOFTWARE_URL = "https://github.com/OntoUML/ontouml-json2graph/"

# Formats for saving graphs supported by RDFLib
# https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html#saving-rdf
ALLOWED_GRAPH_FORMATS = ["turtle", "ttl", "turtle2", "xml", "pretty-xml", "json-ld", "ntriples", "nt", "nt11", "n3",
                         "trig", "trix", "nquads"]

# URIs
URI_ONTOLOGY = "https://example.org#"
URI_ONTOUML = "https://w3id.org/ontouml#"