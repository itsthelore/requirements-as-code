---
schema_version: 1
id: RAC-KV6KFK645AMN
type: requirement
tags: [user-facing, security, trust, mcp, grounding]
---
# Requirement: Trust Model and Artifact-as-Attack-Surface

## Status

Proposed

Classification: `[user-facing]` — assurance the grounding layer is not an
injection vector. Scoped to the v0.23.0 hardening release (WS11).

## Problem

A coding agent ingests artifact content as authoritative grounding. The
read-only MCP server protects the store, not the agent: a poisoned artifact or a
hostile pull request can carry text engineered to steer the consuming agent away
from recorded decisions. This was the red-team's highest-priority gap — we
assert artifacts are trustworthy without recording why, or giving a consumer any
signal to distinguish a reviewed decision from an unreviewed draft.

## Requirements

- [REQ-001] The release MUST document the trust model in `SECURITY.md`: artifact content is authoritative because it passed human PR review; the read-only MCP server protects the store, not the agent; unreviewed or machine-ingested content is out of scope and MUST NOT be treated as trusted (ADR-065).
- [REQ-002] `SECURITY.md` MUST state the threat (a poisoned artifact or hostile PR can attempt to steer the consuming agent) and the mitigation (PR review plus the `rac doctor` injection flag).
- [REQ-003] `rac doctor` MUST flag instruction-like / injection-style content in artifacts (shared with WS3).
- [REQ-004] `get_artifact` MUST surface a review/trust signal — at minimum the artifact's status — additively, so a consumer can distinguish a reviewed-`Accepted` decision from a `Proposed`/draft artifact.
- [REQ-005] Nothing in this release may auto-edit artifact content; the trust boundary remains human PR review.

## Acceptance Criteria

- The trust model is documented in `SECURITY.md`.
- `rac doctor` flags a planted injection-style fixture, and a test asserts the
  flag fires.
- `get_artifact` exposes review status, verified by a test, as an additive
  backward-compatible field.

## Success Metrics

- A user can articulate, from the docs, exactly what the read-only guarantee
  does and does not protect.
- A consumer can tell reviewed decisions apart from drafts via tool output.

## Risks

- A reader mistakes the doctor flag for a guarantee. Mitigation: `SECURITY.md`
  states plainly that PR review is the boundary and the flag is an aid.

## Assumptions

- Front-matter status plus the provenance fields (WS5) carry enough signal to
  power the review/trust distinction without PR-API plumbing this release.

## Related Decisions

- adr-065
- adr-030
- adr-032
- adr-034

## Related Requirements

- rac-provenance-surfacing
- rac-doctor-diagnostic-validator

## Related Roadmaps

- v0.23.0-hardening
