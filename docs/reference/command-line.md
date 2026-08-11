# Command-line reference

Display the authoritative parser output for the installed version with:

```console
python -m json2graph.decode --help
```

## Input and output

| Option | Default | Meaning |
| --- | --- | --- |
| `-i`, `--input_path` | Required | Existing JSON file, or an existing directory when `--decode_all` is used. |
| `-o`, `--output_path` | Current working directory | Directory for generated files; created when absent. |
| `-a`, `--decode_all` | Disabled | Process direct `*.json` children of the input directory. |
| `-f`, `--format` | `ttl` | RDF serialization and output extension. |
| `-l`, `--language` | No language tag | Language tag applied to source `name` literals. |
| `-m`, `--model_only` | Disabled | Remove project and diagrammatic resources. |

Supported serialization names are `turtle`, `ttl`, `turtle2`, `xml`,
`pretty-xml`, `json-ld`, `ntriples`, `nt`, `nt11`, `n3`, `trig`, `trix`, and
`nquads`.

## Identity

| Option | Default | Meaning |
| --- | --- | --- |
| `-u`, `--base-uri`, `--base_uri` | None | Use one explicit absolute base URI. |
| `--base-uri-with-content-id` | None | Treat the URI as a parent and append the deterministic content UUID. |

The identity options are mutually exclusive. With neither option, the decoder
uses `urn:uuid:<content-uuid>#`.

## Corrections, policies, and diagnostics

| Option | Default | Accepted values or effect |
| --- | --- | --- |
| `-c`, `--correct` | Disabled | Enable the legacy class and property correction pass. |
| `-s`, `--silent` | Disabled | Suppress progress and legacy validation log messages, but not Python warnings or exceptions. |
| `--invalid-stereotype-policy` | `preserve` | `preserve`, `omit`, `error` |
| `--invalid-cardinality-policy` | `preserve` | `preserve`, `repair`, `error` |
| `--unresolved-model-element-policy` | `omit` | `preserve`, `omit`, `error` |
| `--path-order-policy` | `warn` | `warn`, `comment` |
| `--property-assignment-policy` | `warn` | `warn`, `comment` |
| `--transformation-metadata` | `none` | `none`, `embedded`, `sidecar` |

See [Policies and configuration](../concepts/policies.md) for the consequence of
each accepted value.

## Informational options

| Option | Meaning |
| --- | --- |
| `-h`, `--help` | Display parser help and exit. |
| `-v`, `--version` | Display the installed project version and exit. |

## Output naming

The model filename is `<input-stem>.<format>`. Sidecar provenance, when
selected, is always Turtle and is named `<input-stem>.provenance.ttl` beside the
model file.
