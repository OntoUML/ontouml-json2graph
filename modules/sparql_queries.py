""" All SPARQL queries used for decoding the JSON. """

GET_ELEMENT_AND_TYPE = """
PREFIX ontouml: <https://w3id.org/ontouml#>
SELECT ?inst_type
WHERE {
    ?inst_type rdfs:subClassOf+ ontouml:OntoumlElement .
    ?inst_id rdf:type ?inst_type .
}"""
