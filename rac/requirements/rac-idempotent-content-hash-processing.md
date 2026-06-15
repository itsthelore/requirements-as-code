---
schema_version: 1
id: RAC-KV6KFP1QDRB0
type: requirement
tags: [internal, performance, determinism, hashing]
---
# Requirement: Idempotent Content-Hash Processing

## Status

Proposed

Classification: `[internal]`. Scoped to the v0.23.0 hardening release (WS8,
core only).

## Problem

Lore's buyers are teams with years of accumulated decisions, not a tiny repo on
day one. The inner loop and CI must stay fast on an ICP-sized corpus, and the
determinism guarantee that underpins the eval benchmark (WS1) needs reinforcing:
the same input must always produce identical derived output. Today, validation,
eval, and doctor reprocess everything every run.

## Requirements

- [REQ-001] RAC MUST content-hash every artifact and short-circuit unchanged artifacts in validation, eval, and doctor processing.
- [REQ-002] Derived output MUST be idempotent and byte-stable: the same input produces identical output, underpinning WS1's byte-stability.
- [REQ-003] The short-circuit MUST apply to CLI processing only and MUST NOT introduce a persistent cache into the MCP serving path, which re-reads per call (ADR-032).
- [REQ-004] Resumability and crash-safe incremental job machinery (partial-run resumption, two-phase persistence) are explicitly out of scope; there is no long-running interruptible operation yet.

## Acceptance Criteria

- Re-running on an unchanged repo does near-zero work and is provably idempotent
  (test).
- Changing one artifact reprocesses only that artifact.
- Outputs are byte-stable across runs.

## Success Metrics

- CI and the inner loop stay fast on a large, realistic corpus.

## Risks

- A hash short-circuit could mask a real change. Mitigation: hash over full
  artifact content; cover with tests that change one artifact and assert only it
  reprocesses.

## Assumptions

- The source of truth stays in markdown/git; derived data is always rebuildable.

## Related Decisions

- adr-032
- adr-011
- adr-013

## Related Requirements

- rac-grounding-eval-benchmark

## Related Roadmaps

- v0.23.0-hardening
