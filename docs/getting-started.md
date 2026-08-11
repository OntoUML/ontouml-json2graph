# Getting started

`ontouml-json2graph` requires Python 3.10 or newer. Install the published
package with:

```console
pip install ontouml-json2graph
```

## Convert one file

The command-line interface writes the transformed graph to the current working
directory by default. The default serialization is Turtle (`ttl`).

```console
python -m json2graph.decode -i my_ontology.json
```

Choose another output directory or serialization with `-o` and `-f`:

```console
python -m json2graph.decode -i my_ontology.json -o results -f json-ld
```

The output filename uses the input stem and the selected format as its
extension. The command above writes `results/my_ontology.json-ld`.

## Decode in Python

Use the library interface when Python code should receive an RDFLib `Graph`:

```python
from json2graph.library import decode_json_project

graph = decode_json_project("my_ontology.json")
```

Use `decode_json_model` instead when diagrammatic and project-level resources
should be removed.

## Choose the output scope

- Complete-project decoding retains model, project, and supported diagrammatic
  resources.
- Model-only decoding retains domain-level model resources, including
  enumeration literals, and removes project and diagrammatic resources.

Both routes use the same transformation core and policy defaults.

## Know the input boundary

The decoder expects the OntoUML JSON structure. It parses JSON but does not
perform JSON Schema validation. UTF-8 is preferred; input that cannot be decoded
as UTF-8 is retried as CP1252 and produces a warning.

Complete-project output is not necessarily lossless. Read
[Limitations and diagnostics](concepts/limitations.md) before relying on the RDF
to reconstruct a source document.

Continue with the [command-line guide](guides/command-line.md),
[Python library guide](guides/python-library.md), or
[Policies and configuration](concepts/policies.md).
