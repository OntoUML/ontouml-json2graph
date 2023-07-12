# The OntoUML JSON2Graph Transformation

The OntoUML JSON2Graph (ontouml-json2graph) decodes a JSON file that complies with
the [ontouml-schema](https://github.com/OntoUML/ontouml-schema) (e.g., the ones exported by
the [ontouml-vp-plugin](https://github.com/OntoUML/ontouml-vp-plugin)) to a graph file that complies with
the [ontouml-vocabulary](https://github.com/OntoUML/ontouml-vocabulary). Optionally, the user can enable basic semantic
and syntactical verifications to improve the transformation results.

This application was constructed with [RDFLib](https://rdflib.readthedocs.io/en/stable/) using Python 3.11.4. The
generated graph file can be serialized in the diverse formats supported by the RDFLib, which are Turtle, RDF/XML,
JSON-LD, N-Triples, Notation-3, Trig, Trix, and N-Quads.

## Installing and Executing

You need to [download and install Python](https://www.python.org/downloads/) to execute the ontouml-json2graph
transformation tool. To install all necessary dependencies, run the following command on the terminal inside the
project's folder:

```text
pip install -r requirements.txt
```

For executing the software, run the following command on the terminal inside the project's folder, where path_to_json
must be substituted for the location of the catalog's directory on your computer:

```text
python main.py path_to_json
```

## Arguments

All available ontouml-models-tools arguments can be observed below.

```text
usage: ontouml-json2graph [-h] [-f {turtle,ttl,turtle2,xml,pretty-xml,json-ld,ntriples,nt,nt11,n3,trig,trix,nquads}] [-l LANGUAGE] [-c] [-s] [-v] json_file                     
                                                                                                                                                                                
OntoUML JSON2Graph Decoder. Version: 2023.07.07                                                                                                                                 
                                                                                                                                                                                
positional arguments:                                                                                                                                                           
  json_file             The path of the JSON file to be encoded.                                                                                                                
                                                                                                                                                                                
options:                                                                                                                                                                        
  -h, --help            show this help message and exit                                                                                                                         
  -f {turtle,ttl,turtle2,xml,pretty-xml,json-ld,ntriples,nt,nt11,n3,trig,trix,nquads}, --format {turtle,ttl,turtle2,xml,pretty-xml,json-ld,ntriples,nt,nt11,n3,trig,trix,nquads}
                        Format to save the decoded file. Default is 'ttl'.                                                                                                      
  -l LANGUAGE, --language LANGUAGE                                                                                                                                              
                        Language tag for the ontology's concepts. Default is None.                                                                                              
  -c, --correct         Enables syntactical and semantic validations and corrections.                                                                                           
  -s, --silent          Silent mode. Does not present validation warnings and errors.                                                                                           
  -v, --version         Print the software version and exit.   
```

## Basic Syntactical and Sematic Validation

Classes' constraints validations:

- isExtensional must be null when the class's stereotype is not 'collective'
- order must be greater than one when the class's stereotype is 'type'
- class's order must be one when the class's stereotype is not 'type'
- class must have stereotype 'type' when no stereotype is informed and when its isPowertype attribute is true
- class's isPowertype must be false when class's stereotype is not 'type'

Properties' validations:

- Reports invalid property stereotypes (i.e., stereotypes different from ontouml:begin or ontouml:end.
- Reports invalid stereotype use for class stereotype

## Authorship

- [Pedro Paulo Favato Barcelos](https://orcid.org/0000-0003-2736-7817) [[GitHub](https://github.com/pedropaulofb)] [[LinkedIn](https://www.linkedin.com/in/pedropaulofavatobarcelos/)]

Please get in touch with this software's contributors using the provided links or *
*preferably [open an issue](https://github.com/OntoUML/ontouml-json2graph/issues)** in case of doubts or problems found.
