[![Project Status - Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
![GitHub - Release Date - PublishedAt](https://img.shields.io/github/release-date/ontouml/ontouml-json2graph)
![GitHub - Last Commit - Branch](https://img.shields.io/github/last-commit/ontouml/ontouml-json2graph/main)
![PyPI - Project](https://img.shields.io/pypi/v/ontouml-json2graph)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ontouml-json2graph?label=pypi%20downloads)
![Language - Top](https://img.shields.io/github/languages/top/ontouml/ontouml-json2graph)
![Language - Version](https://img.shields.io/pypi/pyversions/ontouml-json2graph)
![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/ontouml/ontouml-json2graph)
![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/OntoUML/ontouml-json2graph/badge)
![License - GitHub](https://img.shields.io/github/license/ontouml/ontouml-json2graph)

# The OntoUML JSON2Graph Transformation

<p align="center"><img src="https://raw.githubusercontent.com/OntoUML/ontouml-json2graph/main/json2graph/resources/logo-json2graph.png" width="740"></p>

The OntoUML JSON2Graph (ontouml-json2graph) decodes a JSON file that complies with the [ontouml-schema](https://w3id.org/ontouml/schema) (e.g., the ones exported by the [ontouml-vp-plugin](https://github.com/OntoUML/ontouml-vp-plugin)) to a graph file that complies with the [ontouml-vocabulary](https://github.com/OntoUML/ontouml-vocabulary).

When transforming a model, you can choose to represent only the core concepts of the model or include all of its information, including diagrammatic elements, as part of the knowledge graph. Additionally, users have the choice to enable basic semantic and syntactical verifications, ensuring enhanced and accurate transformation results.

This application was developed using the [RDFLib](https://rdflib.readthedocs.io/en/stable/) and Python 3.11. The generated graph file can be serialized in the diverse [formats supported by the RDFLib](https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html#saving-rdf), which are Turtle, RDF/XML, JSON-LD, N-Triples, Notation-3, Trig, Trix, and N-Quads.

**📦 PyPI Package:**
The transformation is conveniently [available as a PyPI package](https://pypi.org/project/ontouml-json2graph/), which allows users to use it as an executable script or import it as a library into other Python projects.

**📚 Documentation:**
For inquiries and further information, please refer to the [comprehensive docstring-generated documentation](https://w3id.org/ontouml/json2graph/docs) available for this project.

## Contents

<!-- TOC -->

* [The OntoUML JSON2Graph Transformation](#the-ontouml-json2graph-transformation)
    * [Contents](#contents)
    * [Installation](#installation)
    * [Usage](#usage)
        * [Execution Modes](#execution-modes)
            * [Executing as a Script](#executing-as-a-script)
            * [Importing as a Library](#importing-as-a-library)
        * [Arguments](#arguments)
        * [Input and Output](#input-and-output)
        * [OntoUML Vocabulary and gUFO](#ontouml-vocabulary-and-gufo)
    * [Basic Syntactical and Sematic Validation](#basic-syntactical-and-sematic-validation)
    * [Permanent URLs and Identifiers](#permanent-urls-and-identifiers)
    * [Related Projects](#related-projects)
    * [Development Contribution](#development-contribution)
    * [Author](#author)

<!-- TOC -->

## Installation

Before using the OntoUML JSON2Graph Decoder, you need to [download and install Python](https://www.python.org/downloads/).
To install the application you simply need to perform the following command:

```text
pip install ontouml-json2graph
```

All dependencies will be installed automatically, and you will be ready to use the ontouml-json2graph package.

## Usage

### Execution Modes

After being installed, the OntoUML JSON2Graph Decoder can be used as an **executable script** or **imported as a library** into another Python project.

The output of the transformation, i.e., the graph file, will be saved into a directory named `results` in the same path in which the software was executed.

#### Executing as a Script

For executing the software, run the following command on the terminal inside the project's folder:

```txt
python -m json2graph.decode [path_to_json] [OPTIONAL ARGUMENTS]
```

#### Importing as a Library

In the current version, users have access to a single class: **ontouml_json2graph**. To use it, include the following line in your python module:

```python
from json2graph.decode import decode_ontouml_json2graph
```

More information about how to use the decode function [can be accessed in its documentation](https://dev.ontouml.org/ontouml-json2graph/autoapi/json2graph/index.html#submodules).

### Arguments

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

### Input and Output

This software's **input** is a JSON file that complies with the [OntoUML Schema](https://w3id.org/ontouml/schema). This JSON file can be obtained from the [ontouml-vp-plugin](https://w3id.org/ontouml/vp-plugin)'s export feature. The JSON2Graph Decoder was tested to guarantee its compatibility with the JSON generated by the plugin's [version 0.5.3](https://w3id.org/ontouml/vp-plugin/v0.5.3).

The transformation's **output** corresponds to the OntoUML Model serialized as a graph. The saved file information is described by the [OntoUML Vocabulary](https://w3id.org/ontouml/vocabulary) and can be saved in the [different formats that are supported by the RDFLib](https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html#saving-rdf). This output graph may contain the model's diagrammatic information or not, depending on the user's provided arguments. The [OntoUML Vocabulary documentation](https://dev.ontouml.org/ontouml-vocabulary/#mozTocId376551) contains a userge overview, presenting information about all available elements, and about how to use them, including examples of SPARQL queries.

Both the input and output of the software are built upon the same metamodel, the [OntoUML Metamodel](https://w3id.org/ontouml/metamodel), which facilitates the conversion between different representations.

### OntoUML Vocabulary and gUFO

The ontouml-vp-plugin has a feature that enables an ontology to be transformed from OntoUML to a graph format. This feature is called the [Model Transformation to OWL with gUFO](https://github.com/OntoUML/ontouml-vp-plugin/#model-transformation-to-owl-with-gufo).
**[gUFO](https://nemo-ufes.github.io/gufo/)** is a lightweight implementation of the OntoUML's underlying foundational ontology, the Unified Foundational Ontology (UFO).

Even though an ontology represented in gUFO and in the OntoUML Vocabulary are both suitable for Semantic Web OWL 2 DL applications, these two representations are different and were created with different purposes.

gUFO is intended for reuse in the definition of UFO-based lightweight ontologies. Reuse of gUFO consists in instantiating and/or specializing the various entities defined in the ontology, inheriting from it the domain-independent distinctions of UFO. A key feature of UFO (and hence, gUFO) is that it includes two taxonomies: one with classes whose instances are individuals (classes in this taxonomy include gufo:Object, gufo:Event) and another with classes whose instances are types (classes in this taxonomy include gufo:Kind, gufo:Phase, gufo:Category).

Differently, the OntoUML Vocabulary was created to support the serialization, exchange, publishing of OntoUML as linked data, and to be used in Semantic Web applications.
Models in this format are machine-readable resources intended to support the needs of tool developers and researchers, enabling the performance of complex analysis using the SPARQL querying language with no need for additional software. In addition, as it contains the concrete elements (i.e., diagrammatic data such as diagrams and diagram elements) of OntoUML projects, it can also be used to fully reconstruct the original models.

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

- Repository: [https://w3id.org/ontouml/json2graph](https://w3id.org/ontouml/json2graph)
- Documentation: [https://w3id.org/ontouml/json2graph/docs](https://w3id.org/ontouml/json2graph/docs)
- Releases:
    - All releases: [https://w3id.org/ontouml/json2graph/releases](https://w3id.org/ontouml/json2graph/releases)
    - Latest release: [https://w3id.org/ontouml/json2graph/latest](https://w3id.org/ontouml/json2graph/latest)
    - Specific release: https://w3id.org/ontouml/json2graph/v<n>, where \<n\> represents the version number (e.g., '1.0.0')

## Related Projects

- **[OntoUML Metamodel](https://w3id.org/ontouml/metamodel)
  **: Implementation-independent OntoUML Metamodel. Unlike the UML profile, this version is independent of UML and presents only the concepts officially supported in the language. This metamodel covers the abstract and concrete syntaxes of the language and serves as the reference for all projects in the [OntoUML as a Service (OaaS)](https://ceur-ws.org/Vol-2969/paper29-FOMI.pdf) ecosystem, including its different model serializations.

- **[OntoUML Vocabulary](https://w3id.org/ontouml/vocabulary)
  **: An OntoUML Metamodel's serialization in Turtle (ttl) format. This vocabulary supports the serialization, exchange, and publishing of OntoUML models as graphs that can be used for Semantic Web and Linked Data applications.

- **[OntoUML Schema](https://w3id.org/ontouml/schema)
  **: An OntoUML Metamodel's serialization in JSON format. The JSON is a format better suited for manipulation within software code. It supports the exchange of models between modeling tools and the OntoUML server, providing model intelligent services.

- **[ontouml-vp-plugin](https://w3id.org/ontouml/vp-plugin)
  **: The OntoUML Plugin for Visual Paradigm adds features designed for OntoUML modelers to any version of the Visual Paradigm - a modeling editor that provides a [free for non-commercial version](https://www.visual-paradigm.com/download/community.jsp). These features range from enabling OntoUML stereotypes in class diagrams to model verification and transformation.

## Development Contribution

We encourage you to contribute to the development of this software.

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

Feel free to get in touch using the provided links. For questions, contributions, or to report any problem, you can *
*[open an issue](https://github.com/OntoUML/ontouml-json2graph/issues)** at this repository.
