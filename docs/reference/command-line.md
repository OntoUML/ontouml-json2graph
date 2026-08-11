# Command-line reference

The complete reference below is generated from the current command-line parser
by running `python -m json2graph.decode --help` at a fixed display width. Do not
edit the included help file manually; regenerate it with the repository
documentation builder.

```{literalinclude} cli-help.txt
:language: text
```

## Output naming

The model filename is `<input-stem>.<format>`. Sidecar provenance, when
selected, is always Turtle and is named `<input-stem>.provenance.ttl` beside the
model file.
