# Python library guide

Use the library interface when Python code should receive an RDFLib `Graph`
instead of relying on the command-line file-writing workflow.

The supported interface has three entry points:

- `decode_json_project` returns model and diagrammatic information.
- `decode_json_model` returns model information without diagrammatic content.
- `save_graph_file` writes an RDFLib graph using a supported serialization.

Library decoding supports in-memory provenance but does not implicitly create a
provenance sidecar. File-writing behavior remains an explicit application or
command-line responsibility.

See the [Python API reference](../reference/python-api.rst) for signatures and
parameter documentation. Transformation semantics are organized under
[behavior](../concepts/transformation.md), [policies](../concepts/policies.md),
and [limitations](../concepts/limitations.md).
