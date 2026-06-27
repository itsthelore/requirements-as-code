---
schema_version: 1
id: RAC-KW47GGS85CKG
type: decision
---
# ADR-087: External-Reference Relationships (Jira and Beyond)

## Status

Proposed

## Category

Technical

## Context

Change traceability in many organisations runs through Jira. Without a typed way
to link an artifact to its ticket, teams jam ticket IDs into prose and the link
goes stale; with one, the corpus gains regulator-grade traceability — "this ADR
implements this Jira" becomes a typed edge.

The relationship registry (ADR-055) is code-defined and enforces each edge's
range to in-corpus artifact types; resolution is deterministic and Git-native
(ADR-016). A Jira ticket is not an artifact, so it cannot be a normal edge
target. ADR-052 defers fully custom, repo-declared edge kinds. ADR-010 already
recognises that untyped targets exist and are legitimate. The need is a typed,
lintable link to an *external* system that deliberately does not resolve to a
local artifact.

## Decision

Introduce an **external-reference relationship family**: code-defined edges whose
target is an external identifier rather than an in-corpus artifact, explicitly
exempt from artifact-range resolution (the ADR-010 untyped-target shape,
generalised).

- The first instance is `related_jira`, declared via a `## Related Jira` section.
  The mechanism is general so future external edges (for example GitHub issues or
  ServiceNow records) reuse the same exemption rather than each re-litigating it.
- **Syntax:** one item per line — a Jira key (`PROJ-1234`) or a full Jira URL.
- **Engine scope is format-lint only.** `rac validate` checks the syntax
  deterministically and offline and flags malformed entries; it never contacts
  Jira and an external reference never affects whether the corpus is valid beyond
  its format.
- **Existence and state checks** (does the ticket exist; is it in an allowed
  state) require a token and a network call and therefore live in the
  `lore-atlassian` satellite (ADR-090), never in the engine (ADR-002, ADR-073).
  Enforcement is at write time, not agent time (ADR-067).
- **Graph export** surfaces the external edge as a typed edge marked unresolved
  or external (ADR-074), so graph backends see the relationship without the
  engine pretending to resolve it.

## Consequences

### Positive

- Typed, lintable change traceability the corpus can carry and the graph export
  can surface, without a database and without a network dependency in the engine.
- A reusable external-reference shape means the next external system is additive,
  not another exemption debate.

### Negative

- An external edge is only as fresh as the satellite's optional state check; the
  engine alone cannot tell a stale ticket from a live one.
- A second class of edge (external-target) adds nuance to the registry and the
  graph export contract.

### Risks

- Pressure to make the engine call Jira "just to validate the ticket".
  Mitigation: the engine is format-lint only by decision; state checks are
  satellite-only (ADR-002).
- The exemption is read as the door to arbitrary custom edge kinds (ADR-052).
  Mitigation: the family is code-defined here, not repo-declared; new external
  kinds are added by ADR, like any registry change.

## Alternatives Considered

### Keep Jira IDs in prose

No typed edge; mention the ticket in the body.

#### Disadvantages

- Untyped, unlinted, and invisible to the graph export; the link rots and
  traceability is unverifiable.

### Force a Jira edge into the existing artifact-range registry

Add `related_jira` with a normal range.

#### Disadvantages

- A Jira ticket is not an artifact; range resolution would always fail. The
  external-target exemption is the correct mechanism, not a workaround.

### A full custom-relationship-type system

Let repos declare arbitrary edge kinds in config.

#### Disadvantages

- Deferred by ADR-052; far more surface than the need. A code-defined external
  family covers the real requirement now.

The external-reference family with `related_jira` as its first instance is
selected.

## Relationship to Other Decisions

- ADR-055, ADR-016: extends the code-defined registry with an external-target
  edge class; resolution stays deterministic and Git-native for in-corpus edges.
- ADR-010: generalises the untyped-target exemption to typed external references.
- ADR-052: custom repo-declared kinds remain deferred; this family is
  code-defined.
- ADR-074: external edges surface in the typed graph export, marked unresolved.
- ADR-067, ADR-073, ADR-090: write-time format-lint in the engine; token-gated
  state checks in `lore-atlassian`.
- ADR-085: an instance of the rule — the network half is a satellite, the
  deterministic half is the engine, decided for everyone.
