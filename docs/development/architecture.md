# Architecture

The package separates supported interfaces, transformation orchestration,
element decoding, and shared behavior.

## Source responsibilities

- `json2graph.library` exposes the supported Python interface.
- `json2graph.decode` coordinates command-line and library transformations.
- `json2graph.decoder` converts OntoUML project, model, and diagram objects.
- `json2graph.modules` provides argument handling, validation, policies,
  metadata, input/output, resource identity, and graph utilities.
- `json2graph.resources` contains packaged metadata, logos, and OntoUML
  Vocabulary resources.
- `json2graph.tests` contains regression fixtures and executable behavior checks.

## Data flow

Both public interfaces reach the same transformation orchestration. The
orchestrator loads the source document, initializes configuration, delegates
element conversion, applies cross-cutting behavior, and returns the graph. The
command-line route additionally manages batch selection, serialization, and
optional provenance sidecars.

The [Python API reference](../reference/python-api.rst) defines the supported
library boundary. Internal modules remain implementation details and are not
published as an API tree.
