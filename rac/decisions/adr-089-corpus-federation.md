---
schema_version: 1
id: RAC-KW47GKNGVVBT
type: decision
---
# ADR-089: Corpus Federation — Parent Corpus and `## inherits`

## Status

Proposed

## Category

Architecture

## Context

Many repositories share one firm-wide set of standards. Without inheritance,
every repository reinvents the firm's ADRs, and there is no single place to hold
rules that should apply across an organisation.

Federation is the single genuine semantic change among the enterprise asks, and
the deepest. Today the corpus is single-tree: one canonical root per repository
(ADR-018) with git `main` as the only source of truth (ADR-080); cross-repository
references do not resolve; relationships are local and Git-native (ADR-016,
ADR-055). A parent-corpus mechanism touches resolution, validation, and export at
once.

## Decision

Federation is **accepted in principle but deferred in mechanism, and
design-partner-gated**. The engine will gain a parent-corpus resolver under a
future design and its own implementing ADR, written when a design partner commits
to it — not speculatively. This decision records the bar that any such design must
clear.

Non-negotiable constraints on any future federation design:

- **Never gated behind "enterprise."** If federation is sound it is sound for the
  solo developer; it changes resolution for everyone or not at all (ADR-085).
  Gating a truth-model change behind a commercial label is precisely the mode
  failure this programme refuses.
- **Deterministic and offline** (ADR-002): parent resolution reads materialised
  bytes — a pinned submodule, a vendored bundle, or a path — never a live network
  fetch inside the validate path.
- **Single canonical state preserved per repo** (ADR-018, ADR-080): a parent is
  an inherited, read-only layer; the child's `main` remains its own truth;
  overrides are explicit, not implicit precedence.
- **Git-native and human-readable** (ADR-016, ADR-055): inheritance is declared
  in Markdown (a `## inherits` section) plus a pinned source reference; no
  database and no hidden index becomes the source of truth.
- **Provenance preserved:** an inherited artifact is always attributable to its
  source corpus, never silently absorbed.

Until the implementing design lands, `## inherits` is unrecognised, and the
profile scaffold (ADR-088) emits no parent declaration.

## Consequences

### Positive

- The bar is recorded now, so the eventual design cannot quietly become an
  enterprise-only fork or a network dependency.
- Firms get a credible answer ("yes, under these constraints, when we build it
  with you") without the project paying for a speculative, partner-less design.

### Negative

- The highest-value enterprise lever stays unbuilt in the near term; shared
  standards remain a manual or satellite concern until then.

### Risks

- Pressure to ship federation quickly and gated behind "enterprise". Mitigation:
  this ADR forbids enterprise-gating and binds the constraints in advance.
- Scope creep toward a live cross-repo index. Mitigation: materialised-bytes,
  offline, Git-native are recorded constraints, not preferences.

## Alternatives Considered

### Build federation now, speculatively

Design and ship the resolver ahead of a design partner.

#### Disadvantages

- The deepest change on the roadmap, built without a real corpus to test the
  override and provenance semantics against; high risk of rework.

### Enterprise-only federation

Offer inheritance as a paid/enterprise capability.

#### Disadvantages

- Gates a resolution-model change behind a label — the forbidden mode (ADR-085).
  Rejected.

### Never federate

Keep every corpus single-tree forever.

#### Disadvantages

- Leaves a real, repeated enterprise need (firm-wide standards) permanently
  unmet.

Accept in principle, defer the mechanism, bind the constraints, gate on a design
partner.

## Relationship to Other Decisions

- ADR-018, ADR-080: federation must preserve the single canonical state per repo;
  a parent is read-only and inherited.
- ADR-016, ADR-055: inheritance stays Git-native and human-readable; no database.
- ADR-002: parent resolution is offline over materialised bytes.
- ADR-085: federation is decided for everyone, never an enterprise gate.
- ADR-088: the profile scaffold stays hollow on the parent line until this ships.
