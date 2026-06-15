---
schema_version: 1
id: RAC-KV6KFQZHDFR5
type: requirement
tags: [user-facing, demo, grounding, proof]
---
# Requirement: Obey-Demo Grounding Proof

## Status

Proposed

Classification: the release's success proof. Scoped to the v0.23.0 hardening
release (T3-A).

## Problem

The release's definition of done is an outcome, not green CI: a real coding
agent must demonstrably stop relitigating a recorded decision. An automated
multi-agent CI harness to prove this would be non-deterministic, slow, costly,
and only half-automatable in a week. What is needed instead is one reproducible,
honest manual demonstration.

## Requirements

- [REQ-001] The release MUST produce one reproducible manual demonstration: a fixture or partner-representative repo with an `Accepted` ADR forbidding a change, a real coding agent wired to the four tools, and a prompt that would violate the decision.
- [REQ-002] The demonstration MUST capture a recording or log showing the agent consulted Lore and did NOT perform the forbidden change.
- [REQ-003] The demonstration MUST ship with written, repeatable steps and MUST NOT be a CI gate.
- [REQ-004] The release MUST NOT build an automated multi-agent CI harness; this manual obey-demo supersedes that intent.
- [REQ-005] Results MUST be genuine; faked or staged outcomes are unacceptable.

## Acceptance Criteria

- A recorded, repeatable demo plus written steps exists.
- It is explicitly a manual smoke, not a CI gate, with no faked results.
- Setup notes for additional agents (Cursor, Codex) MAY be documented but are
  not required.

## Success Metrics

- The release success criterion is met: a real or partner-representative agent
  does not relitigate the forbidden decision after consulting Lore.

## Risks

- A single demo may not generalize. Mitigation: source the scenario from a real
  or partner-representative decision and document the steps so it can be re-run
  and extended.

## Assumptions

- A real coding agent wired to the four read-only tools is sufficient to
  demonstrate grounding without bespoke harness infrastructure.

## Related Decisions

- adr-034
- adr-065

## Related Requirements

- rac-artifact-trust-model
- rac-grounding-eval-benchmark

## Related Roadmaps

- v0.23.0-hardening
