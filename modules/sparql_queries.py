""" All SPARQL queries used for decoding the JSON. """

GET_ELEMENT_AND_TYPE = """
PREFIX ontouml: <https://w3id.org/ontouml#>
SELECT ?inst_type
WHERE {
    ?inst_type rdfs:subClassOf+ ontouml:OntoumlElement .
    ?inst_id rdf:type ?inst_type .
}"""

# Returns only when property_stereotype equals begin or end
GET_CLASS_STEREOTYPE_ATTRIBUTE_STEREOTYPE = """
PREFIX ontouml: <https://w3id.org/ontouml#>
SELECT DISTINCT ?class_id ?class_stereotype ?property_id ?property_stereotype
WHERE {
    ?class_id rdf:type ontouml:Class .
    ?class_id ontouml:stereotype ?class_stereotype  .
    ?property_id rdf:type ontouml:Property .
    ?property_id ontouml:stereotype ?property_stereotype .
    ?property_id ontouml:propertyType ?class_id .
    VALUES ?property_stereotype {ontouml:begin ontouml:end}
}"""
