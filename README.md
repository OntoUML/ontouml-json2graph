[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8214977.svg)](https://doi.org/10.5281/zenodo.8214977)
[![Project Status - Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
![GitHub - Release Date - PublishedAt](https://img.shields.io/github/release-date/ontouml/ontouml-json2graph)
![GitHub - Last Commit - Branch](https://img.shields.io/github/last-commit/ontouml/ontouml-json2graph/main)
![PyPI - Project](https://img.shields.io/pypi/v/ontouml-json2graph)
![Language - Version](https://img.shields.io/pypi/pyversions/ontouml-json2graph)
![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/ontouml/ontouml-json2graph)
![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/OntoUML/ontouml-json2graph/badge)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/OntoUML/ontouml-json2graph/main.svg)](https://results.pre-commit.ci/latest/github/OntoUML/ontouml-json2graph/main)
![License - GitHub](https://img.shields.io/github/license/ontouml/ontouml-json2graph)

# OntoUML JSON2Graph

<p align="center"><img src="https://raw.githubusercontent.com/OntoUML/ontouml-json2graph/main/json2graph/resources/logo-json2graph.png" width="740" alt="OntoUML JSON2Graph logo"></p>

`ontouml-json2graph` transforms OntoUML JSON projects into RDF graphs that use
the [OntoUML Vocabulary](https://w3id.org/ontouml/vocabulary). It can retain
project and diagrammatic information or produce a model-only graph.

Use the command-line interface to convert files directly, or the supported
Python API to obtain an RDFLib `Graph`. The package supports Python 3.10 or
newer.

## Installation

```console
pip install ontouml-json2graph
```

## Command-line quick start

Convert one JSON file to Turtle in the current directory:

```console
python -m json2graph.decode -i my_ontology.json
```

Choose an output directory and serialization explicitly:

```console
python -m json2graph.decode -i my_ontology.json -o results -f json-ld
```

Convert every `.json` file directly inside a directory:

```console
python -m json2graph.decode -a -i models -o results
```

Display all supported options and their defaults with:

```console
python -m json2graph.decode --help
```

## Python quick start

```python
from json2graph.library import decode_json_project, save_graph_file

graph = decode_json_project("my_ontology.json")
save_graph_file(graph, "my_ontology.ttl", "ttl")
```

The supported public API consists of:

- `decode_json_project` for model and diagrammatic information;
- `decode_json_model` for model-only output; and
- `save_graph_file` for explicit RDF serialization.

## Important behavior

- Without an explicit base URI, the package derives a deterministic
  `urn:uuid:` namespace from the parsed JSON content.
- The default policies preserve invalid stereotypes and cardinality source
  values where possible, omit unresolved diagrammatic `modelElement`
  references, and warn about information that the vocabulary cannot represent.
- The `correct` option enables a legacy set of class and property corrections.
  It is independent of the explicit policy options.
- Input is decoded as UTF-8, with a warned CP1252 fallback. The package expects
  the OntoUML JSON structure but does not perform JSON Schema validation.
- Complete-project output is not a guarantee of lossless reconstruction. Path
  point order, non-empty `propertyAssignments`, and legacy diagrammatic
  `Text.value` content have no direct normative representation in OntoUML
  Vocabulary 1.1.1.

See the [documentation](https://w3id.org/ontouml/json2graph/docs) for the
complete CLI and Python guides, policy consequences, diagnostics, limitations,
and 1.x-to-2.0 migration guidance.

## Development

Install the project and development dependencies with Poetry:

```console
poetry install
```

Run the primary validation commands from the repository root:

```console
poetry check --strict --lock
poetry run python update_documentation.py
poetry run pytest
poetry run pre-commit run --all-files
```

Generated Sphinx HTML is written to `docs/_build/html` and is not committed.

## Project links

- [Documentation](https://w3id.org/ontouml/json2graph/docs)
- [PyPI](https://pypi.org/project/ontouml-json2graph/)
- [Releases](https://w3id.org/ontouml/json2graph/releases)
- [Issue tracker](https://github.com/OntoUML/ontouml-json2graph/issues)
- [OntoUML Schema](https://w3id.org/ontouml/schema)
- [OntoUML Vocabulary](https://w3id.org/ontouml/vocabulary)
- [OntoUML Metamodel](https://w3id.org/ontouml/metamodel)

## Author and organization

The author of `ontouml-json2graph` is
[Pedro Paulo Favato Barcelos](https://orcid.org/0000-0003-2736-7817).

The project is maintained in the
[OntoUML organization](https://github.com/OntoUML), linked to the
[Semantics, Cybersecurity & Services Group](https://www.utwente.nl/en/eemcs/scs/)
at the [University of Twente](https://www.utwente.nl/), The Netherlands.

The software is distributed under the [Apache License 2.0](LICENSE).
