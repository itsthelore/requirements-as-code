---
schema_version: 1
id: RAC-KV68XS3J7P6C
type: roadmap
tags: [structure, org, distribution]
---
# Repo Extraction Programme

## Status

Planned

## Context

ADR-063 records the decision to adopt a small multi-repo topology under the
`itsthelore` organisation: extract the standalone components and keep the
engine, its shipped resources, and its governing corpus in
`itsthelore/requirements-as-code`. This programme sequences those extractions.
It is a non-versioned `future/` item because the work is structural and
cross-cutting, not a feature release on the current series.

The three targets differ sharply in risk. `decisiongrounding` imports no
engine code and can move with no consumer impact. The examples are
pedagogical and partly still being built liftable (v0.20.1). The GitHub
Actions are the only target whose move is consumer-breaking: extraction
changes the `uses:` path that downstream workflows reference, so it must come
last and behind a versioned cutover.

## Outcomes

- Each target component lives in its own `itsthelore` repository, depending
  only on the published `requirements-as-code` package or the public `rac`
  CLI — never on engine internals — with no coupling regression.
- The engine repository carries only the engine, its shipped resources
  (skills, templates, hooks), and the dogfood corpus.
- Every consumer-facing reference (action `uses:` paths, docs, CI workflows)
  is updated, and no stranded reference is left behind.

## Initiatives

### Initiative 1 — Extract `decisiongrounding` (reference migration)

The cleanest target and the pattern for the rest. Move `decisiongrounding/`
to `itsthelore/decisiongrounding` with history preserved, carrying its own
`pyproject.toml`, tests, LICENSE, Makefile, and its `decisions/` ADRs
(DG-ADR-0001 onward). It already treats `rac` as an external CLI on `PATH`, so
no code changes are needed; remove the directory from the monorepo and update
any references to it (including the v0.20.1 roadmap's "mirrors
`decisiongrounding/`" note, which becomes a cross-repo reference).

### Initiative 2 — Extract examples to `itsthelore/rac-examples`

Build the SDK examples sub-project liftable per v0.20.1 (own `pyproject.toml`
depending on the published package), then graduate it together with
`examples/` into `itsthelore/rac-examples`. The examples depend on the
published package or the public CLI, proving the surface from outside the
source tree.

### Initiative 3 — Extract the GitHub Actions (versioned cutover)

Move `validate-action/action.yml` and the root `action.yml` (Watchkeeper) to
`itsthelore/rac-actions` (or per-action repos). This changes the `uses:` path
consumers reference, so it ships behind a versioned cutover: publish the new
location, document the new `uses:` reference, leave a deprecation note for the
old path, and update this repository's own `.github/workflows/` to the new
location. ADR-058 governs the validation action and moves with it.

## Constraints

- No engine behaviour change and no change to the public surface: this is a
  topology move, not a feature.
- Distribution names stay frozen (ADR-036, ADR-039): PyPI
  `requirements-as-code`, CLI `rac`, server identity `lore`.
- The engine and MCP server stay one package (ADR-029); they are not part of
  any extraction.
- Each extraction preserves history (`git filter-repo` or `git subtree`,
  decided per repo) rather than copying files flat.

## Non-Goals

- Extracting `lore-web` — deferred by ADR-063 until its Portal-shell vendoring
  has a publish/vendor contract.
- Renaming the package, CLI, or server.
- Creating the org repositories as part of this corpus task; the repos are
  created when each initiative is executed.

## Implementation Contract

- Each extraction produces a new `itsthelore/<repo>` populated by a
  history-preserving move, the source directory removed from the monorepo, and
  all in-repo and documentation references updated.
- The actions extraction additionally ships a versioned cutover: new `uses:`
  reference documented, old path deprecated, this repo's workflows updated.
- After each extraction the engine repository's `rac validate rac/`,
  `rac relationships rac/ --validate`, and `rac review rac/` gates stay green.

## Success Measures

- All three targets are extracted and consume only the published package or
  public CLI; no extracted repo imports engine internals.
- No issue traces to a stranded `uses:` path or a missing relocated component.
- The engine repository's corpus gates remain green throughout.

## Assumptions

- The `itsthelore` organisation can host the sibling repositories and the
  maintainer can create and permission them when each initiative runs.
- `decisiongrounding` continues to consume `rac` only as an external CLI on
  `PATH`, so its move needs no code change (DG-ADR-0001 holds).
- The published `requirements-as-code` package remains the dependency surface
  for the examples, and the public `rac` CLI for the actions — neither needs
  engine internals.
- `lore-web` stays in this repository until its vendoring contract exists, so
  no Portal-shell drift-guard breaks during this programme.

## Risks

- **Stranded action references.** Consumers pinned to the old `uses:` path
  break. Mitigation: actions move last, behind a versioned cutover with a
  deprecation note.
- **Cross-repo drift.** Extracted components lag the engine contract.
  Mitigation: each pins a published-package or CLI version and depends on no
  internals.
- **History loss.** A flat copy discards provenance. Mitigation: the contract
  mandates a history-preserving move.

## Related Decisions

- adr-063
- adr-058

## Related Roadmaps

- v0.20.1-python-sdk-docs

## Related Requirements

- rac-growth-extensibility
