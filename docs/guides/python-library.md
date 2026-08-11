# Python library guide

The supported library interface exposes two decoders and one graph-writing
utility from `json2graph.library`.

## Decode a complete project

```python
from json2graph.library import decode_json_project

graph = decode_json_project("my_ontology.json")
```

`decode_json_project` returns model, project, and supported diagrammatic
resources in an RDFLib `Graph`.

## Decode model information only

```python
from json2graph.library import decode_json_model

graph = decode_json_model("my_ontology.json")
```

`decode_json_model` removes project and diagrammatic resources while retaining
domain-level model resources, including enumeration literals.

## Write a graph

Library decoding does not write a model file. Serialize explicitly with:

```python
from json2graph.library import save_graph_file

save_graph_file(graph, "my_ontology.ttl", "ttl")
```

The accepted syntax names are listed in the
[Python API reference](../reference/python-api.rst) and match the CLI's supported
serializations.

## Configure decoding

Both decoding functions accept the same optional controls:

- `base_uri` and `append_content_hash` for resource identity;
- `language` for language-tagging source `name` literals;
- `correct` for the legacy class and property correction pass;
- policies for invalid stereotypes, invalid cardinalities, unresolved
  diagrammatic `modelElement` references, path-point order, and
  `propertyAssignments`; and
- `transformation_metadata` for absent or embedded provenance.

When `base_uri` is omitted, a deterministic `urn:uuid:` namespace is derived
from the parsed JSON. When `append_content_hash=True`, a supplied `base_uri` is
treated as a parent and the content UUID is appended.

Library decoding accepts `transformation_metadata="none"` or `"embedded"`.
Embedded mode returns a new graph containing model and provenance triples and
adds a generation timestamp. Sidecar mode is rejected because it requires a
file-writing operation and is available only through the CLI.

Path-order comments have no effect on model-only output because it contains no
paths. Property-assignment handling applies only to elements that remain in the
returned graph.

## Handle warnings and errors

Library calls suppress the transformation's informational and legacy correction
logs. They still emit Python warnings for encoding fallback, normalization,
policy decisions, and representational loss. Callers can filter or capture these
warnings with Python's `warnings` module.

Invalid option values and `error` policies raise `ValueError` or a specialized
`ValueError` subclass. File and JSON decoding failures propagate to the caller.

See the [Python API reference](../reference/python-api.rst) for signatures and
parameter documentation, and [Policies and configuration](../concepts/policies.md)
for exact policy consequences.
