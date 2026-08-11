# Migrating from 1.x to 2.0

Use this guide when moving an existing command, integration, or generated-data
workflow from a 1.x release to 2.0.

The migration is organized around the observable changes that can affect users:

- deterministic default resource identity and explicit base-URI modes;
- complete-project and model-only behavior;
- independent policies for invalid and non-representable source content;
- warnings and errors associated with those policies;
- optional embedded or sidecar transformation provenance;
- OntoUML Vocabulary 1.1.1 alignment; and
- current command-line and Python interfaces.

Before comparing generated graphs, identify the resource-identity mode and
transformation policies used by the 1.x workflow. Then consult the
[transformation overview](concepts/transformation.md),
[policies](concepts/policies.md), and [limitations](concepts/limitations.md)
sections for the corresponding 2.0 behavior.
