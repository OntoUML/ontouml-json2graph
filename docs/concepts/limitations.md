# Limitations and diagnostics

## Input validation and encoding

The decoder parses JSON and expects the OntoUML JSON structure. It does not run
the OntoUML JSON Schema or another structural validation step before traversing
the document. Malformed JSON, absent required structures, unexpected types, and
unsupported values can therefore raise parser or runtime errors during
decoding.

UTF-8 is attempted first. A Unicode decoding failure triggers a CP1252 retry and
`JSONEncodingFallbackWarning`. The parsed data is otherwise handled identically.

## Information without a normative representation

OntoUML Vocabulary 1.1.1 does not directly represent:

- order among a Path's point values;
- non-empty `propertyAssignments` maps; or
- content stored in the legacy diagrammatic `Text.value` field.

Path order and property assignments can be recorded as non-normative
`rdfs:comment` text. Those comments do not extend the vocabulary and should not
be interpreted as a formal graph structure. A non-empty `Text.value` is omitted
with `UnsupportedTextValueWarning`; an empty value is omitted silently.

## Invalid and incomplete source values

Explicit policies control invalid stereotypes, invalid cardinalities, and
unresolved diagrammatic `modelElement` references. A non-error policy can
preserve or omit affected information and emits a warning. An `error` policy
raises an exception and prevents command-line file output.

Invalid `width` or `height` values that are not non-negative integers are logged
and omitted. Valid zero values are retained as `xsd:nonNegativeInteger`, in
accordance with OntoUML Vocabulary 1.1.1.

When initial RDF serialization fails, the file writer retries after normalizing
invalid URI references. If writing still fails with an operating-system error,
the error is propagated.

## Diagnostic channels

The transformation uses two diagnostic channels:

- logger messages for progress, supplied defaults, legacy validation and
  correction activity, and some malformed values; and
- Python warnings for encoding fallback, stereotype normalization and policy
  decisions, cardinality repair, unresolved references, shared batch identity,
  and non-representable source information.

CLI `--silent` and the library's silent execution suppress logger progress and
legacy validation messages. They do not suppress Python warnings or exceptions.
Applications can capture or filter warnings through Python's `warnings` module.

## Reconstruction qualification

Complete-project output retains project and supported diagrammatic resources,
but it is not a guarantee of byte-for-byte or semantically lossless source
reconstruction. JSON formatting, object-key order, null fields, and unsupported
or policy-omitted information are not preserved as source JSON. Non-normative
comments can retain selected source context, but consumers need explicit logic
to interpret them.

See [Policies and configuration](policies.md) for exact consequences and
[Transformation overview](transformation.md) for processing order.
