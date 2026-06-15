---
schema_version: 1
id: RAC-KV6KFJ7BERWG
type: requirement
tags: [internal, robustness, parser, traversal, mcp]
---
# Requirement: Parser and Bounded-Traversal Robustness

## Status

Proposed

Classification: `[internal]` — invisible, but the server must never crash in
front of a partner. Scoped to the v0.23.0 hardening release (WS4).

## Problem

The MCP server sits in an agent's critical path. A malformed artifact, an
oversized field, or a pathological relationship graph must never crash, hang, or
exhaust memory. The front-matter/markdown parser currently has no input-size
caps and no fuzz coverage, and while `get_related` is one-hop and the ADR-033
response budget bounds its output, those guarantees are not yet asserted against
adversarial input.

## Requirements

- [REQ-001] The parser MUST cap input sizes per-file and per-field, and MUST guard any user-defined regex/pattern features against catastrophic backtracking (ReDoS).
- [REQ-002] A single malformed artifact MUST degrade gracefully — reported and skipped — and MUST NOT crash `get_artifact` / `search_artifacts` or fail CI uninformatively.
- [REQ-003] The release MUST add fuzz/property tests over the parser covering malformed YAML, oversized fields, unicode, deep nesting, and binary junk.
- [REQ-004] `get_related` output MUST remain bounded by the ADR-033 response budget, with a deterministic result cap and ordering (relationship type, then ascending artifact id) and a backward-compatible truncation signal.
- [REQ-005] When any cap truncates output, the kept items MUST be selected and ordered deterministically so output stays byte-stable.
- [REQ-006] Any future multi-hop traversal MUST add explicit depth, frontier, visited-set, and work-budget caps before shipping; this release does not add multi-hop traversal.

## Acceptance Criteria

- Parser fuzz tests pass; a malformed artifact yields a clear `doctor` error and
  does not crash `get_artifact` / `search_artifacts`.
- Graph fuzz fixtures — cycles, self-references, deep chains, and a high-fan-out
  hub — all terminate within budget with well-formed, deterministically
  truncated output and the truncation signal set.
- A test asserts traversal/serving over an adversarial graph completes within
  the budget with no unbounded time or memory.

## Success Metrics

- No input — malformed file or pathological graph — can hang, crash, or OOM the
  serving path.

## Risks

- Over-tight caps could reject legitimately large artifacts. Mitigation: caps
  are configurable with safe defaults proven against adversarial input.

## Assumptions

- The ADR-033 budget already bounds response size; this release proves and
  extends that guarantee rather than re-architecting serving.

## Related Decisions

- adr-033
- adr-055
- adr-032

## Related Requirements

- rac-doctor-diagnostic-validator

## Related Roadmaps

- v0.23.0-hardening
