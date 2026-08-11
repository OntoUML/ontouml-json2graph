# Limitations and diagnostics

The transformation parses JSON and expects the OntoUML JSON structure used by
the project. It does not perform JSON Schema validation before decoding.

Some source information has no direct normative representation in the OntoUML
Vocabulary. The main cases are:

- order among path points;
- non-empty `propertyAssignments`; and
- the legacy diagrammatic `Text.value` field.

Depending on the available policy, the transformer can warn, omit affected
information, preserve source values, raise an error, or add a non-normative
comment. A non-normative comment records context but does not extend the
OntoUML Vocabulary or make the source information structurally representable.

Warnings are also used for recovered text encoding and malformed or invalid
values handled by a non-error policy. Errors stop the affected transformation.

See [Policies and configuration](policies.md) for the control categories and
[Transformation overview](transformation.md) for their place in the conversion
flow.
