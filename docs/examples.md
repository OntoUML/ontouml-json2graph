# Examples

Run these examples from `docs/examples` after installing `ontouml-json2graph`.
The small project is a quick starting point; the catalog model shows a larger
conversion. The commands write results under `docs/examples/output`, which can
be removed after use.

## Minimal example

The [minimal project](examples/minimal-project.json) contains one class. The
documentation tests execute this same input and the following two examples.

```{literalinclude} examples/minimal-project.json
:language: json
```

Run the command-line conversion:

```{literalinclude} examples/cli-usage.txt
:language: console
```

Or use the Python library:

```{literalinclude} examples/library-usage.py
:language: python
```

## Catalog example: Simple Genealogy Ontology

The [complete JSON project](examples/catalog/genealogy2013.json) comes from the
[OntoUML Model Catalog](https://github.com/OntoUML/ontouml-models). The
[source record](examples/catalog/genealogy2013-source.txt) gives the pinned
revision, upstream JSON blob, and its **CC BY 4.0** license. This JSON is
complete and executable; the short excerpts below are for reading only.

A class in the source:

```{literalinclude} examples/catalog/genealogy2013.json
:language: json
:lines: 117-122
```

The source also defines a material relation, `parentOf`:

```{literalinclude} examples/catalog/genealogy2013.json
:language: json
:lines: 259-264
```

### Convert the model

To produce model-only Turtle, run:

```console
python -m json2graph.decode -i catalog/genealogy2013.json -o output --model_only --silent
```

This writes `output/genealogy2013.ttl`, with classes such as `Person`, `Parent`,
and `Registration`, and the `parentOf` relation. In Python, obtain an RDFLib
graph directly:

```python
from json2graph.library import decode_json_model

graph = decode_json_model("catalog/genealogy2013.json")
```

### Complete project versus model only

Run these commands separately (both write the same output filename):

```console
python -m json2graph.decode -i catalog/genealogy2013.json -o output --silent
python -m json2graph.decode -i catalog/genealogy2013.json -o output --model_only --silent
```

The corresponding Python calls are `decode_json_project("catalog/genealogy2013.json")`
and `decode_json_model("catalog/genealogy2013.json")`.

| Output | Domain model elements | Packages | Project | Diagram and views |
| --- | --- | --- | --- | --- |
| Complete project | Yes | Yes | Yes | Yes |
| Model only | Yes | No | No | No |

The complete source contains diagram Paths with ordered points. A complete
conversion emits an expected `PathPointOrderWarning` because the OntoUML
Vocabulary cannot represent their order. The graph is still written. Model-only
conversion removes the Paths and avoids this warning. `--silent` hides log
messages, **not Python warnings**. See [Limitations and diagnostics](concepts/limitations.md)
for details.

### Choose a base URI

To place generated resources under an explicit namespace:

```console
python -m json2graph.decode -i catalog/genealogy2013.json -o output --model_only --base-uri https://example.org/genealogy# --silent
```

The equivalent Python call is:

```python
graph = decode_json_model("catalog/genealogy2013.json", base_uri="https://example.org/genealogy#")
```

### Generate provenance

The CLI can write transformation metadata to a separate Turtle file:

```console
python -m json2graph.decode -i catalog/genealogy2013.json -o output --model_only --transformation-metadata sidecar --silent
```

This writes `output/genealogy2013.ttl` and
`output/genealogy2013.provenance.ttl`. The Python library supports embedded
transformation metadata with `transformation_metadata="embedded"`; it does not
write a sidecar file.

For additional options, see the [command-line guide](guides/command-line.md),
[Python library guide](guides/python-library.md), and
[Policies and configuration](concepts/policies.md).
