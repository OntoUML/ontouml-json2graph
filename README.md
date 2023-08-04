![PyPI](https://img.shields.io/pypi/v/ontouml-json2graph) ![PyPI - Downloads](https://img.shields.io/pypi/dm/ontouml-json2graph?label=pypi%20downloads)
 ![GitHub top language](https://img.shields.io/github/languages/top/ontouml/ontouml-json2graph)
 ![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/ontouml/ontouml-json2graph) ![GitHub last commit (branch)](https://img.shields.io/github/last-commit/ontouml/ontouml-json2graph/main)
 ![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/ontouml/ontouml-json2graph) ![GitHub](https://img.shields.io/github/license/ontouml/ontouml-json2graph)

# The OntoUML JSON2Graph Transformation

<p align="center"><img src="https://raw.githubusercontent.com/OntoUML/ontouml-json2graph/main/json2graph/resources/logo-json2graph.png" width="740"></p>


The OntoUML JSON2Graph (ontouml-json2graph) decodes a JSON file that complies with the [ontouml-schema](https://w3id.org/ontouml/schema) (e.g., the ones exported by the [ontouml-vp-plugin](https://github.com/OntoUML/ontouml-vp-plugin)) to a graph file that complies with the [ontouml-vocabulary](https://github.com/OntoUML/ontouml-vocabulary). Optionally, the user can enable basic semantic and syntactical verifications to improve the transformation results.

Being [released as a package](https://pypi.org/project/ontouml-json2graph/), the transformation can be used as an executable script or imported as a library into another Python project.

This application was constructed with [RDFLib](https://rdflib.readthedocs.io/en/stable/) using Python 3.11.4. The generated graph file can be serialized in the diverse [formats supported by the RDFLib](https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html#saving-rdf), which are Turtle, RDF/XML, JSON-LD, N-Triples, Notation-3, Trig, Trix, and N-Quads.

This project [complete docstring-generated documentation](https://w3id.org/ontouml/json2graph/docs) is available for inquiries.

## Contents

<!-- TOC -->
* [The OntoUML JSON2Graph Transformation](#the-ontouml-json2graph-transformation)
  * [Contents](#contents)
  * [Installation](#installation)
  * [Usage](#usage)
    * [Executing as a Script](#executing-as-a-script)
    * [Importing as a Library](#importing-as-a-library)
  * [Arguments](#arguments)
  * [Basic Syntactical and Sematic Validation](#basic-syntactical-and-sematic-validation)
  * [Permanent URLs and Identifiers](#permanent-urls-and-identifiers)
  * [Related Projects](#related-projects)
  * [Development Contribution](#development-contribution)
  * [Author](#author)
<!-- TOC -->

## Installation

You need to [download and install Python](https://www.python.org/downloads/) to use the OntoUML JSON2Graph Decoder.
To install the application you simply need to perform the following command:

```text
pip install ontouml-json2graph
```

All dependencies will be automatically installed, and you are ready to use the ontouml-json2graph package.

## Usage

After being installed, the OntoUML JSON2Graph Decoder can be used as an **executable script** or **imported as a library** into another Python project.

The output of the transformation, i.e., the graph file, will be saved into a directory named `results` in the same path in which the software was executed.

### Executing as a Script

For executing the software, run the following command on the terminal inside the project's folder:

```txt
python -m json2graph.decode [path_to_json] [OPTIONAL ARGUMENTS]
```

### Importing as a Library

In its current version, a single class is available to users: **ontouml_json2graph**. To use it, include the following line in your python module: 

```python
from json2graph.decode import ontouml_json2graph
```

More information about how to use the decode function [can be accessed in its documentation](https://dev.ontouml.org/ontouml-json2graph/autoapi/json2graph/index.html#submodules).

## Arguments

The only mandatory argument is `path_to_json`, which must be substituted for the input file's location on your computer. Optional arguments provide additional features. All available ontouml-json2graph arguments can be observed below.

```text
usage: ontouml-json2graph [-h]
                          [-f {turtle,ttl,turtle2,xml,pretty-xml,json-ld,ntriples,nt,nt11,n3,trig,trix,nquads}]
                          [-l LANGUAGE] [-c] [-s] [-u BASE_URI] [-m] [-v]
                          json_file

OntoUML JSON2Graph Decoder. Version: 1.0.1

positional arguments:
  json_file             The path of the JSON file to be encoded.

options:
  -h, --help            show this help message and exit
  -f {turtle,ttl,turtle2,xml,pretty-xml,json-ld,ntriples,nt,nt11,n3,trig,trix,nquads}, --format {turtle,ttl,turtle2,xml,pretty-xml,json-ld,ntriples,nt,nt11,n3,trig,trix,nquads}
                        Format to save the decoded file. Default is 'ttl'.
  -l LANGUAGE, --language LANGUAGE
                        Language tag for the ontology's concepts. Default is 'None'.
  -c, --correct         Enables syntactical and semantic validations and corrections.
  -s, --silent          Silent mode. Does not present validation warnings and errors.
  -u BASE_URI, --base_uri BASE_URI
                        Base URI of the resulting graph. Default is 'https://example.org#'.
  -m, --model_only      Keep only model elements, eliminating all diagrammatic data from output.
  -v, --version         Print the software version and exit.
```

## Basic Syntactical and Sematic Validation

- Class validations:
    - Reports Class with incompatible attributes isExtensional (not 'null') and isPowertype (set as 'True').
    - Sets Class stereotype as 'collective' when the Class's stereotype is 'null' and its isExtensional attribute is 'True'.
    - Sets Class stereotype as 'type' when the Class's stereotype is 'null' and its isPowertype attribute is 'True'.
    - Removes the Class's isExtensional attribute if the Class's stereotype is not 'collective'.
    - Sets the Class's isPowertype attribute as 'False' if the Class's stereotype is not 'type'.
    - Sets the Class's order attribute to '1' if the Class's stereotype is not 'type' and its order different than '1'.
    - Sets the Class's order attribute to '2' if the Class's stereotype is 'type' and its order is '1'.
    - Reports mandatory Class stereotype missing.
- Stereotype validations:
    - Reports invalid Class stereotype assigned (i.e., assigned stereotype is not in enumeration class ClassStereotype).
    - Reports invalid Relation stereotype assigned (i.e., assigned stereotype is not in enumeration class RelationStereotype).
    - Reports invalid Property stereotype assigned (i.e., assigned stereotype is not in enumeration class PropertyStereotype).
- Property validations:
    - Reports invalid assertion when a Property stereotype is related to a Class that is known not to be of stereotype 'event'.
    - Sets Class stereotype as 'event' when it is originally 'null' and the class is related to a Property with stereotype.

## Permanent URLs and Identifiers

- Repository: https://w3id.org/ontouml/json2graph
- Documentation: https://w3id.org/ontouml/json2graph/docs
- Releases:
    - Latest version: https://w3id.org/ontouml/json2graph/latest
    - Specific version: https://w3id.org/ontouml/json2graph/v<n>, where \<n\> is a version number (e.g., '1.0.0')

## Related Projects

- **[OntoUML Metamodel](https://w3id.org/ontouml/metamodel)
  **: Implementation-independent OntoUML Metamodel. Unlike the UML profile, this version is independent of UML and presents only the concepts officially supported in the language. This metamodel covers the abstract and concrete syntaxes of the language and serves as the reference for all projects in the [OntoUML as a Service (OaaS)](https://ceur-ws.org/Vol-2969/paper29-FOMI.pdf) ecosystem, including its different model serializations.


- **[OntoUML Vocabulary](https://w3id.org/ontouml/vocabulary)
  **: An OntoUML Metamodel's serialization in Turtle (ttl) format. This vocabulary supports the serialization, exchange, and publishing of OntoUML models as graphs that can be used for Semantic Web and Linked Data applications.


- **[OntoUML Schema](https://w3id.org/ontouml/schema)
  **: An OntoUML Metamodel's serialization in JSON format. The JSON is a format better suited for manipulation within software code. It supports the exchange of models between modeling tools and the OntoUML server, providing model intelligent services.

## Development Contribution

We encourage you to contribute with the development of this software.  

The dependencies to develop this software are not the same as the ones to execute it. Hence, it is necessary run the following command on the terminal inside the project's folder to install all necessary dependencies:

```text
pip install -r requirements.txt
```

The software uses the metadata provided in its `pyproject.toml` file to present information to users. If any change is made to that file, the `setup_metadata.py` file, located inside the project's root folder must be executed to update the transformation's data. 

The ontouml-json2graph package was developed using test-driven-based development. Multiple tests are available inside the following folder: ontouml-json2graph/json2graph/tests.

Documentation regarding the text [is also available](https://dev.ontouml.org/ontouml-json2graph/autoapi/json2graph/tests/index.html).

## Author

This project is maintained by the [Semantics, Cybersecurity & Services (SCS) Group](https://www.utwente.nl/en/eemcs/scs/) of the [University of Twente](https://www.utwente.nl/), The Netherlands. Its developer is:

- [Pedro Paulo Favato Barcelos](https://orcid.org/0000-0003-2736-7817) [[GitHub](https://github.com/pedropaulofb)] [[LinkedIn](https://www.linkedin.com/in/pedropaulofavatobarcelos/)]

Feel free to get in contact using the links provided. For questions, contributions, or to report any problem, you can **[open an issue](https://github.com/OntoUML/ontouml-json2graph/issues)** at this repository.
