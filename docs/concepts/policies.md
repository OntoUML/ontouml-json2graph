# Policies and configuration

Transformation controls are documented by purpose rather than by the interface
through which they are supplied.

## Correction behavior

The legacy correction switch enables the established syntactic and semantic
correction behavior. It is separate from the policy controls below.

## Invalid input policies

Independent policies govern invalid stereotypes, invalid cardinalities, and
unresolved `modelElement` references. Each policy determines whether affected
source information is preserved, omitted, repaired where supported, or treated
as an error.

## Non-representable information

Separate policies govern ordered path points and non-empty
`propertyAssignments`. These controls determine whether the transformation only
warns or also adds a non-normative explanatory comment.

## Identity and provenance

Resource-identity options determine the generated base URI. Provenance options
determine whether transformation metadata is absent, embedded in the graph, or
written as a command-line sidecar.

Interface-specific names and accepted values belong in the
[command-line reference](../reference/command-line.md) and
[Python API reference](../reference/python-api.rst). Consequences that cannot be
eliminated through configuration belong in
[Limitations and diagnostics](limitations.md).
