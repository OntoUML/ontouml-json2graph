# Maintaining the documentation

Sphinx sources live under `docs/`. Generated HTML is written to
`docs/_build/html` and is not committed.

Run the repository documentation builder from the repository root:

```console
poetry run python update_documentation.py
```

The builder performs a clean Sphinx build with warnings treated as errors and
nitpicky reference checking enabled. A successful run therefore verifies the
page hierarchy, internal references, and generated Python API page before it
replaces the local HTML output.

Documentation is divided by responsibility:

- task-oriented instructions belong in `guides/`;
- shared transformation semantics belong in `concepts/`;
- interface definitions belong in `reference/`;
- release-transition guidance belongs in `migration.md`; and
- contributor material belongs in `development/`.

The root README is the package and repository entry point. Detailed behavior
should have one primary location in the Sphinx sources and be linked from the
README rather than maintained independently in both places.
