""" All SPARQL queries used for decoding the JSON. """

NOT_PROJECT_ELEMENTS = """
PREFIX ontouml: <https://w3id.org/ontouml#>
SELECT DISTINCT ?inst
WHERE {
    ?onto_class rdfs:subClassOf+ ontouml:OntoumlElement .
    ?inst rdf:type ?onto_class .
    FILTER NOT EXISTS {?inst rdf:type ontouml:Project . }
}"""

GET_ELEMENT_AND_TYPE = """
PREFIX ontouml: <https://w3id.org/ontouml#>
SELECT DISTINCT ?inst_type
WHERE {
    ?inst_type rdfs:subClassOf+ ontouml:OntoumlElement .
    ?inst_id rdf:type ?inst_type .
}"""