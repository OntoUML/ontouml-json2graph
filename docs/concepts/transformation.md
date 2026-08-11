# Transformation overview

The transformation converts an OntoUML JSON document into an RDF graph that uses
terms from the OntoUML Vocabulary.

At a high level, the implementation:

1. loads the JSON document;
2. resolves the resource namespace;
3. converts model and, when requested, diagrammatic elements while applying the
   configured handling for invalid or non-representable content;
4. adds transformation provenance when requested; and
5. returns an RDFLib graph or serializes it through the command-line workflow.

Complete-project and model-only decoding share the same transformation core.
They differ in whether diagrammatic resources remain in the result.

Configuration choices are grouped in [Policies and configuration](policies.md).
Known representational boundaries and diagnostic behavior are grouped in
[Limitations and diagnostics](limitations.md).
