---
schema_version: 1
id: RAC-KV6KFN3HPGS1
type: requirement
tags: [user-facing, provenance, git, mcp]
---
# Requirement: Provenance Surfacing

## Status

Proposed

Classification: `[user-facing]` — the agent can cite who decided and when.
Scoped to the v0.23.0 hardening release (WS5).

## Problem

Lore claims every decision has an accountable human author, but `get_artifact`
does not surface that accountability. An agent grounding on a decision cannot
cite who made it, when, or whether it has moved from proposed to accepted to
superseded. The information already exists in front matter and git history; it
is simply not exposed on the tool surface.

## Requirements

- [REQ-001] `get_artifact` MUST expose, additively and backward-compatibly, at minimum: author(s) plus last-commit author, relevant dates, and status history (Proposed → Accepted → Superseded), sourced from front matter plus git.
- [REQ-002] Provenance MUST be derived from git rather than stored dates in front matter (ADR-045); a `reviewers` front-matter field MAY be used to power the WS11 review signal.
- [REQ-003] Provenance fields SHOULD be surfaced in search/explain output where useful.
- [REQ-004] Full PR-reviewer extraction (squash-merge handling, review threads) is out of scope for this release.

## Acceptance Criteria

- Provenance populates for this release's dogfooded ADRs (ADR-065, ADR-066).
- Tests assert the fields populate from front matter plus git.
- The new fields are additive; existing `get_artifact` consumers are unaffected.

## Success Metrics

- An agent can cite an accountable author and the status of a decision directly
  from tool output.

## Risks

- Git plumbing can balloon. Mitigation: limit to author/last-commit-author,
  dates, and status history; defer PR-reviewer extraction.

## Assumptions

- Git history and front matter carry enough provenance for this release without
  a PR-API integration.

## Related Decisions

- adr-045
- adr-050
- adr-025

## Related Requirements

- rac-artifact-trust-model

## Related Roadmaps

- v0.23.0-hardening
