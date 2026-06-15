---
schema_version: 1
id: RAC-KV6KFH925GH8
type: requirement
tags: [user-facing, doctor, validation, diagnostics]
---
# Requirement: Repository Health Diagnostic (doctor)

## Status

Proposed

Classification: `[user-facing]` — the user runs it on their repo. Scoped to the
v0.23.0 hardening release (WS3).

## Problem

`rac validate` answers pass/fail per file. When a repository is unhealthy — a
broken reference, a dangling relationship, a duplicate id, a decision left
`Accepted` that a later `Accepted` decision supersedes — a user is told *that*
something is wrong but not *where* or *how to fix it*. A new adopter pointing
Lore at a real, years-old corpus needs a single command that diagnoses health
and hands back actionable, paste-ready fixes.

## Requirements

- [REQ-001] RAC MUST provide a `rac doctor` CLI subcommand that diagnoses repository health across malformed/invalid front matter, dangling or broken typed relationships, orphaned artifacts, duplicate ids, schema drift, and deterministically detectable contradictions.
- [REQ-002] For every finding, `rac doctor` MUST print the exact file, the problem, and a paste-ready fix command or edit.
- [REQ-003] `rac doctor` MUST flag relationship cycles and high-fan-out hubs, so authors fix the data that WS4 bounds at runtime.
- [REQ-004] `rac doctor` MUST flag instruction-like / injection-style content — imperative overrides, impersonation of system/agent/tool instructions, or content steering the agent away from recorded decisions (supports WS11).
- [REQ-005] `rac doctor` MUST exit non-zero on errors and zero when only warnings are present, and MUST be deterministic.
- [REQ-006] `rac doctor` MUST be wired into CI alongside existing validation, and SHOULD reuse existing validation and relationship-integrity logic rather than re-deriving it (ADR-055, ADR-049).

## Acceptance Criteria

- `rac doctor` detects each defect class, covered by fixtures, and prints
  actionable fixes.
- Output is deterministic across runs on an unchanged repo.
- A malformed artifact yields a clear `doctor` error rather than crashing
  `get_artifact` / `search_artifacts` (with WS4).

## Success Metrics

- A user can take a real repository from "unknown health" to "clean" by
  following `rac doctor` output without reading RAC's source.

## Risks

- The injection-content heuristic can false-positive. Mitigation: it is a
  reviewable warning for a human, never an auto-edit or a standalone hard
  failure (ADR-065).

## Assumptions

- The validator and relationship engine already detect most defect classes;
  doctor aggregates and explains them with fixes rather than re-implementing.

## Related Decisions

- adr-055
- adr-051
- adr-049
- adr-065

## Related Requirements

- rac-parser-traversal-robustness
- rac-artifact-trust-model

## Related Roadmaps

- v0.23.0-hardening
