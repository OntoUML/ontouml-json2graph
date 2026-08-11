# Command-line guide

Use the command-line interface when the result should be written directly to one
or more RDF files. Inspect the installed interface with:

```console
python -m json2graph.decode --help
```

The command-line workflow is organized around five decisions:

1. Select one JSON file or a directory of JSON files.
2. Select the output directory and RDF serialization.
3. Choose complete-project or model-only output.
4. Choose resource identity, transformation policies, and optional provenance.
5. Review warnings or errors associated with the selected policies.

See the [command-line reference](../reference/command-line.md) for the
authoritative option list. The [policies](../concepts/policies.md) and
[limitations](../concepts/limitations.md) pages explain where configuration can
change the result or report information loss.
