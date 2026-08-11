# Command-line guide

The command-line interface converts one OntoUML JSON file or a directory of
files and writes serialized RDF.

Inspect the interface installed in the current environment with:

```console
python -m json2graph.decode --help
```

## Convert one file

```console
python -m json2graph.decode -i my_ontology.json -o results -f ttl
```

The input must be an existing file whose path contains `.json`. The output
directory defaults to the current working directory and is created when it does
not exist. The output filename is the input stem followed by the selected format
as its extension.

Use `--model_only` to remove project and diagrammatic resources:

```console
python -m json2graph.decode -i my_ontology.json --model_only
```

## Convert a directory

Use `--decode_all` with a directory:

```console
python -m json2graph.decode --decode_all -i models -o results
```

Batch conversion processes the directory's direct `*.json` children in sorted
path order. It does not recurse into subdirectories. Every input uses the same
format, model scope, policies, and provenance mode supplied to the command.

With the default identity mode, each distinct JSON document receives its own
content-derived namespace. `--base-uri-with-content-id` also creates a distinct
content-derived namespace below a supplied parent. An exact `--base-uri` is
shared by every batch output; when more than one file is processed, the command
warns that resources can collide if the graphs are combined.

## Select resource identity

Without a base-URI option, the effective namespace is:

```text
urn:uuid:<content-uuid>#
```

The UUID is derived from canonical parsed JSON. Object-key order and JSON
whitespace do not change it; array order and content do.

Use an explicit namespace with:

```console
python -m json2graph.decode -i my_ontology.json --base-uri https://example.org/my-model#
```

If the value ends in neither `#` nor `/`, the decoder appends `#`. Use a parent
URI plus the content UUID with:

```console
python -m json2graph.decode -i my_ontology.json --base-uri-with-content-id https://example.org/models
```

This produces `https://example.org/models/<content-uuid>#`. The two base-URI
options are mutually exclusive. A content-ID parent cannot contain a query or a
non-empty fragment.

## Configure transformation behavior

The following controls are independent:

- `--correct` enables the legacy class and property correction pass;
- the invalid stereotype, cardinality, and unresolved-reference policies
  select behavior for those input conditions;
- the path-order and property-assignment policies select warning-only or
  non-normative comment behavior; and
- `--transformation-metadata` selects absent, embedded, or sidecar provenance.

See [Policies and configuration](../concepts/policies.md) for exact defaults and
consequences.

## Handle diagnostics

The command reports informational and legacy validation messages through its
logger. `--silent` suppresses those messages, but it does not suppress Python
warnings raised for policy decisions, encoding fallback, or representational
loss, and it does not suppress exceptions.

An `error` policy aborts decoding before the output file is written. Other
policies can warn while still producing a graph. Review
[Limitations and diagnostics](../concepts/limitations.md) for the diagnostic
categories and information-loss boundaries.

See the [command-line reference](../reference/command-line.md) for every option,
default, and serialization name.
