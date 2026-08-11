# Migrating from 1.x to 2.0

Version 2.0 changes defaults and makes previously implicit or lossy behavior
explicit. Review generated graph identifiers and warnings before replacing a
1.x workflow.

## Observable changes

| Area | 1.x behavior | 2.0 behavior |
| --- | --- | --- |
| Python requirement | Python 3.9-compatible package declaration | Python 3.10 or newer |
| Default base URI | Shared `https://example.org#` namespace | Deterministic `urn:uuid:<content-uuid>#` namespace |
| Explicit identity | One supplied base URI | Exact base URI or parent URI plus content UUID |
| Python project decoder | `decode_json_project` incorrectly requested model-only output | `decode_json_project` retains project and diagrammatic resources |
| Invalid stereotypes | Limited validation and implicit emission | Normalized, type-checked, and controlled by `preserve`, `omit`, or `error` |
| Invalid cardinalities | Invalid source handling was not policy-controlled | `preserve`, limited safe `repair`, or `error` |
| Unresolved diagram references | Could materialize unresolved reference stubs | Default `omit`, with `preserve` and `error` alternatives |
| Path-point order | Order was lost without a dedicated policy | Warning by default, with an optional non-normative comment |
| `propertyAssignments` | No dedicated handling | Warning and omission by default, with an optional non-normative comment |
| Metadata and provenance | Basic generator and creation metadata added automatically | Deterministic model-only output by default; optional `embedded` or CLI `sidecar` provenance |
| Vocabulary target | OntoUML Vocabulary 1.1.0 | OntoUML Vocabulary 1.1.1 |
| Diagram dimensions | Vocabulary range excluded zero | Zero-valued width and height use `xsd:nonNegativeInteger` |
| Legacy `Text.value` | Could be mapped to an unsuitable term | Empty values are omitted; non-empty values are warned and omitted |

## Preserve 1.x-style resource identifiers

If a workflow depends on the former shared namespace, request it explicitly:

```console
python -m json2graph.decode -i my_ontology.json --base-uri https://example.org#
```

This can create identifier collisions when outputs are combined, especially in
batch conversion. Prefer the default identity or
`--base-uri-with-content-id <parent>` for content-scoped namespaces.

The Python equivalent is `base_uri="https://example.org#"` without
`append_content_hash`.

## Select policies explicitly

The 2.0 defaults are:

- invalid stereotypes: `preserve`;
- invalid cardinalities: `preserve`;
- unresolved diagrammatic `modelElement` references: `omit`;
- path-point order: `warn`;
- `propertyAssignments`: `warn`; and
- transformation metadata: `none`.

Pin these values in automated workflows when future configuration changes must
not alter behavior. The `correct` option remains separate and defaults to
disabled.

## Review output comparisons

When comparing 1.x and 2.0 graphs:

1. account for the base-URI change or supply the former URI explicitly;
2. compare complete-project output with `decode_json_project` and model-only
   output with `decode_json_model` or `--model_only`;
3. record the selected policies and review emitted warnings;
4. expect OntoUML Vocabulary 1.1.1 datatypes and Text handling; and
5. exclude embedded provenance when deterministic graph equality is required.

Read [Policies and configuration](concepts/policies.md) and
[Limitations and diagnostics](concepts/limitations.md) for the precise 2.0
semantics.
