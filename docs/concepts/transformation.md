# Transformation overview

The transformation converts an OntoUML JSON document into an RDF graph whose
model terms come from the OntoUML Vocabulary.

## Processing flow

For each input document, the implementation:

1. decodes JSON as UTF-8 or, after a Unicode decoding failure, as CP1252;
2. collects non-empty `propertyAssignments` before null cleanup;
3. resolves the effective resource namespace;
4. removes null-valued source fields;
5. applies the unresolved diagrammatic `modelElement` policy;
6. creates resources, general attributes, and type-specific relations;
7. applies correction and policy behavior during decoding;
8. removes project and diagrammatic resources when model-only output is
   requested;
9. applies the `propertyAssignments` policy to resources that remain; and
10. returns an RDFLib graph or writes it through the command-line workflow.

Optional provenance is added in memory for library embedded mode, or during
file output for CLI embedded and sidecar modes.

## Resource identity

The default base URI is deterministic for the parsed JSON document. The decoder
serializes the parsed value as canonical JSON with sorted object keys, compact
separators, preserved array order, and UTF-8 characters. It hashes that text
with SHA-256 and derives a UUIDv5 in the permanent JSON2Graph namespace. The
effective base URI is `urn:uuid:<content-uuid>#`.

An explicit base URI is normalized to end in `#` unless it already ends in `#`
or `/`. Content-scoped explicit identity appends the UUID below a supplied
parent URI. Complete-project and model-only decoding of the same source use the
same namespace.

## Output scope

Complete-project decoding retains the project, model resources, diagrams, and
supported diagrammatic resources. Model-only decoding removes the project,
packages used for containment, diagrams, shapes, views, and paths while keeping
the domain-level model resources.

The transformation also supplies vocabulary-defined default values for missing
non-nullable attributes. This default completion occurs independently of the
`correct` option. The option controls a separate legacy correction pass described
in [Policies and configuration](policies.md).

## Vocabulary use and provenance

The bundled target is OntoUML Vocabulary 1.1.1. Model triples use its terms;
optional explanatory comments use `rdfs:comment`, and optional provenance uses
PROV-O and DCMI terms.

Provenance asserts conformance to the versioned OntoUML Vocabulary only when all
OntoUML predicates and object terms used by the generated model graph are
declared in the bundled vocabulary. That check does not validate the input JSON
or prove that every modeled constraint is satisfied.

See [Limitations and diagnostics](limitations.md) for information that cannot be
represented normatively and for the qualifications on reconstruction.
