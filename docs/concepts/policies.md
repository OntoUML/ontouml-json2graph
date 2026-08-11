# Policies and configuration

Transformation controls are independent unless stated otherwise. In particular,
`correct=True` or `--correct` does not enable or replace the explicit policies.

## Legacy correction behavior

The `correct` option defaults to `False`. When enabled, it applies the existing
class and property semantic checks and corrections, including:

- reconciling class stereotypes with `isExtensional`, `isPowertype`, and
  `order` values;
- assigning corrected default class order after an incompatible value is
  removed; and
- checking stereotyped properties against their owning class and assigning the
  `event` stereotype when that established rule applies.

Missing vocabulary-defined default attributes are supplied whether or not
`correct` is enabled. Explicit policies for invalid stereotypes, cardinalities,
and unresolved references also run independently of it.

## Invalid stereotypes

Assigned Class, Relation, and Property stereotypes are normalized to
lowerCamelCase before validation. A lexical variant that normalizes to a valid
stereotype is emitted canonically and produces a normalization warning.

| Value | Consequence |
| --- | --- |
| `preserve` (default) | Warn and emit the normalized stereotype triple even when it is invalid for the element type. |
| `omit` | Warn and omit only the invalid stereotype triple. |
| `error` | Raise an error and abort before file output. |

## Invalid cardinalities

Valid source forms are `*`, a non-negative integer, `n..m`, and `n..*`, with a
lower bound no greater than a finite upper bound. `*` is normalized to `0..*`,
and an integer `n` is normalized to `n..n`.

| Value | Consequence |
| --- | --- |
| `preserve` (default) | Preserve the original `cardinalityValue`, warn, and omit `lowerBound` and `upperBound`. |
| `repair` | Repair only known separator forms (`n,,m`, `n:m`, `n...m`, and `n..`); otherwise fall back to preserve behavior. |
| `error` | Raise an error and abort before file output. |

Successful repair emits the repaired value and bounds with a repair warning.
Valid and successfully repaired lower and upper bounds use
`xsd:nonNegativeInteger`.

## Unresolved diagrammatic model references

This policy applies only to `modelElement` references on objects contained by
diagrams. It does not validate other reference categories such as `source`,
`target`, `propertyType`, `general`, or `specific`.

| Value | Consequence |
| --- | --- |
| `omit` (default) | Warn, omit the unresolved `modelElement` relation, and preserve the ElementView. |
| `preserve` | Warn, preserve the relation, and materialize the referenced target. |
| `error` | Raise an error and abort before file output. |

## Path-point order

The policy is evaluated only for complete-project output and paths with more
than one point.

| Value | Consequence |
| --- | --- |
| `warn` (default) | Emit point triples without order and warn that the sequence is absent. |
| `comment` | Also add the coordinate sequence as a non-normative `rdfs:comment`; still warn. |

The comment is explanatory text, not a vocabulary-defined ordering structure.

## Property assignments

Only non-empty `propertyAssignments` maps on resources present in the resulting
graph are affected. Null and empty maps are ignored.

| Value | Consequence |
| --- | --- |
| `warn` (default) | Omit the map and warn. |
| `comment` | Add canonical JSON as a non-normative `rdfs:comment`; still warn that no formal semantics were produced. |

Canonical JSON sorts object keys and preserves array order.

## Resource identity

| Configuration | Effective namespace |
| --- | --- |
| No base URI (default) | `urn:uuid:<content-uuid>#` |
| Exact base URI | The supplied absolute URI, normalized with an identifier separator when needed |
| Parent base URI plus content ID | `<parent>/<content-uuid>#` |

The CLI exposes the latter two modes as mutually exclusive options. The Python
API uses `base_uri` and `append_content_hash`.

## Transformation provenance

| Value | Consequence |
| --- | --- |
| `none` (default) | Return or write only the model graph. |
| `embedded` | Add provenance to the same graph; its generation timestamp makes the result non-deterministic. |
| `sidecar` | CLI only: keep the model file unchanged and write `<output-stem>.provenance.ttl`. |

The provenance records the source filename and SHA-256 identifier, software
version, requested and effective identity configuration, output format, and
output-affecting transformation options. It does not record source or output
paths, `silent`, or batch orchestration.
