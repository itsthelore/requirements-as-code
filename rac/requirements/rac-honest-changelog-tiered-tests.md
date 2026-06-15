---
schema_version: 1
id: RAC-KV6KFQ0J1TEM
type: requirement
tags: [internal, changelog, testing, release]
---
# Requirement: Honest Changelog and Tiered Tests

## Status

Proposed

Classification: `[internal]`. Scoped to the v0.23.0 hardening release (WS10).

## Problem

A hardening release needs trust signals and fast feedback loops. The test suite
runs as 24 CI batteries but is not organized into documented tiers a developer
can run locally, and a release with significant deferred scope needs a changelog
that is honest about what shipped, what was deferred, and what the known limits
are — without overclaiming.

## Requirements

- [REQ-001] The release MUST structure the test suite into three documented tiers — a unit-test inner loop, a pre-push verify gate, and a full local CI command — and document each tier's command.
- [REQ-002] The release MUST add a CHANGELOG entry with honest scope notes: what shipped, what is deferred, and known limits — explicitly that the MCP server is pull-based and that code-vs-decision CI enforcement is a future release.
- [REQ-003] The CHANGELOG user-facing headline MUST lead only with the user-facing items (explainable retrieval, `rac doctor`, provenance, the trust model) plus "provably works"; internal plumbing MUST NOT be headlined.
- [REQ-004] The release version MUST be set to `v0.23.0` via the git tag (setuptools-scm); there is no VERSION file to edit.

## Acceptance Criteria

- The three test tiers exist and are documented with their commands.
- The CHANGELOG entry is specific and honest about scope, tradeoffs, and limits.
- The version is bumped to `v0.23.0` at release via tag.

## Success Metrics

- A developer can run the right test tier for the change at hand without reading
  CI internals.
- A reader of the CHANGELOG understands exactly what this release does and does
  not deliver.

## Risks

- Headlining internal items would misrepresent the release as feature-heavy.
  Mitigation: the narrative discipline is encoded in REQ-003.

## Assumptions

- The existing 24-battery structure can be grouped into three documented tiers
  without restructuring the tests themselves.

## Related Decisions

- adr-027
- adr-007

## Related Requirements

- rac-grounding-eval-benchmark

## Related Roadmaps

- v0.23.0-hardening
