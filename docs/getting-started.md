# Getting started

Choose how you want to run the transformation and how much of the OntoUML
project you need in the resulting RDF graph.

## Choose an interface

- Use the [command-line interface](guides/command-line.md) when converting JSON
  files to serialized RDF files.
- Use the [Python library](guides/python-library.md) when an application needs an
  RDFLib `Graph` or controls when and where the graph is written.

## Choose the output scope

The complete-project route includes model and diagrammatic information. The
model-only route removes diagrammatic content and keeps the domain-level model.
Both routes use the OntoUML Vocabulary for the generated RDF.

## Understand behavior before converting

The transformation exposes independent controls for correction, invalid input,
information that the vocabulary cannot represent directly, resource identity,
and optional provenance. Continue with:

- [Transformation overview](concepts/transformation.md)
- [Policies and configuration](concepts/policies.md)
- [Limitations and diagnostics](concepts/limitations.md)
- [Command-line reference](reference/command-line.md)
- [Python API reference](reference/python-api.rst)
