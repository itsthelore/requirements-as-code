---
schema_version: 1
id: RAC-KV6KFGA4PY4C
type: requirement
tags: [user-facing, retrieval, explainability, mcp]
---
# Requirement: Explainable Retrieval

## Status

Proposed

Classification: `[user-facing]` — the user sees *why* the agent grounded. Scoped
to the v0.23.0 hardening release (WS2).

## Problem

When Lore returns a search result, the consuming agent — and the human watching
— sees *that* an artifact was retrieved but not *why*. "No guessing" is a claim
we cannot currently show. Without a deterministic explanation of the match, a
result is opaque: a user cannot tell whether a title, a tag, the body, or a
relationship edge surfaced it, which undermines trust in the grounding.

## Requirements

- [REQ-001] Each `search_artifacts` result MUST carry a deterministic, non-empty `evidence` structure stating which field matched (id / title / path / heading / body), the matched term(s), and the retrieval tier.
- [REQ-002] `get_related` results SHOULD carry evidence identifying the relationship edge (section and target) that surfaced the artifact.
- [REQ-003] The `evidence` structure MUST be an additive, backward-compatible field on the existing tool output; the response schema and tool count MUST NOT otherwise change (ADR-007, ADR-030).
- [REQ-004] RAC MUST provide a `rac find --explain` mode that prints per-stage match attribution for a query.
- [REQ-005] The explanation MUST be a faithful description of the real match reason, derived from the existing token-tier match data (ADR-037, ADR-038), not a separate heuristic.

## Acceptance Criteria

- Every search result includes a non-empty, accurate, deterministic explanation,
  and a test asserts the explanation matches the real match reason.
- `rac find --explain` works from the CLI and prints per-stage attribution.
- Existing MCP contract and golden tests still pass with the additive field
  present (backward compatibility verified).

## Success Metrics

- A user inspecting a result can name the field and term that caused it without
  reading the matcher's source.

## Risks

- Evidence text could be mistaken for a relevance verdict. Mitigation: it
  describes the structural match (field, term, tier), never a semantic judgment
  (ADR-034).

## Assumptions

- The existing matcher already computes the tier and matched terms, so evidence
  is surfacing existing data rather than recomputing it.

## Related Decisions

- adr-037
- adr-038
- adr-007
- adr-030

## Related Requirements

- rac-grounding-eval-benchmark

## Related Roadmaps

- v0.23.0-hardening
