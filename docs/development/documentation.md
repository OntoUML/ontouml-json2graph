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
replaces the local HTML output. It also regenerates
`docs/reference/cli-help.txt` from the current parser before building.

Canonical documentation examples live under `docs/examples/`. Sphinx includes
those files directly, and `json2graph/tests/test_documentation.py` executes the
same CLI and Python examples. Run `poetry run pytest` after changing an example
or interface. The tests also fail when the checked-in CLI help differs from the
current parser output.

Documentation is divided by responsibility:

- task-oriented instructions belong in `guides/`;
- shared transformation semantics belong in `concepts/`;
- interface definitions belong in `reference/`;
- release-transition guidance belongs in `migration.md`; and
- contributor material belongs in `development/`.

The root README is the package and repository entry point. Detailed behavior
should have one primary location in the Sphinx sources and be linked from the
README rather than maintained independently in both places.

## Continuous integration and publication

The `Documentation` GitHub Actions workflow runs the documentation tests and
strict Sphinx builder for pull requests and pushes that can affect the rendered
site. Pull requests validate the documentation without publishing it. A
successful build on `main` uploads `docs/_build/html` and deploys it to the
`github-pages` environment.

Configure the repository's GitHub Pages source as **GitHub Actions** before the
first deployment. Generated HTML remains a workflow artifact and must not be
committed.
