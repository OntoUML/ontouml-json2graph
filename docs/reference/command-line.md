# Command-line reference

The command-line parser is the authoritative source for option names, accepted
values, and defaults. Display the reference for the installed version with:

```console
python -m json2graph.decode --help
```

The options are grouped conceptually as follows:

- input and output selection;
- batch conversion and RDF serialization;
- complete-project or model-only output;
- language and correction behavior;
- exact or content-scoped resource identity;
- invalid stereotype, cardinality, and unresolved-reference policies;
- path-order and property-assignment policies; and
- transformation provenance.

Use the [command-line guide](../guides/command-line.md) for task-oriented
navigation and [Policies and configuration](../concepts/policies.md) for the
behavior shared with the Python interface.
