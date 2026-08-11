# ontouml-json2graph

`ontouml-json2graph` transforms OntoUML JSON projects into RDF graphs that use the
[OntoUML Vocabulary](https://w3id.org/ontouml).

The documentation is organized by task and audience. Start with the introductory
route, use the CLI or Python guide for day-to-day work, and consult the behavior
and reference sections when you need precise transformation or interface details.

## Choose a route

- [Get started](getting-started.md) with the interface and output scope that fit your use case.
- Use the [command-line guide](guides/command-line.md) to convert files or directories.
- Use the [Python library guide](guides/python-library.md) to integrate conversion into Python code.
- Read about [transformation behavior](concepts/transformation.md),
  [policies](concepts/policies.md), and [limitations](concepts/limitations.md).
- Review the [2.0 migration guide](migration.md) when upgrading from a 1.x release.
- Use the [development documentation](development/architecture.md) when maintaining the project.

```{toctree}
:maxdepth: 2
:caption: Start here

getting-started
```

```{toctree}
:maxdepth: 2
:caption: User guides

guides/command-line
guides/python-library
```

```{toctree}
:maxdepth: 2
:caption: Transformation behavior

concepts/transformation
concepts/policies
concepts/limitations
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/command-line
reference/python-api
```

```{toctree}
:maxdepth: 2
:caption: Migration

migration
```

```{toctree}
:maxdepth: 2
:caption: Development

development/architecture
development/documentation
```
