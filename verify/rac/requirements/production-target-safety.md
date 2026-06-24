---
schema_version: 1
id: LV-KVW5PZ658DQK
type: requirement
tags: [user-facing, security, safety, targets, fail-closed]
---
# Requirement: Production Target Safety

## Status

Proposed

Classification: `[user-facing]` — running an autonomously-generated, exploratory
agent against live production is a data-loss / outage vector. Safety must be a
fail-closed, enforced invariant, not an assumption. Derives from the threat model
in LV-ADR-003.

## Problem

`lore-verify` is expected to verify against production targets, but production
cannot be seeded and must not be mutated. Today this lives only as an Assumption in
`faithful-session-to-test` and a risk-mitigation sentence in `v0.2.0-breadth`
("production is verified with read-only / idempotent variants") — a delivery note,
not an enforced control, and circular (the mitigation *is* the unspecified
convention). An autonomous agent driving prod with no enforced write-block is a
data-loss and outage vector. Per RAC ADR-020, a long-lived safety property belongs
in a requirement that outlives any one roadmap item, not in a roadmap risk section
that is consumed and closed.

## Requirements

- [REQ-001] Every target MUST declare whether it is seedable/mutable; a target with no such declaration MUST be treated as non-mutable (fail-closed default).
- [REQ-002] A target marked non-seedable/production MUST default to a write-blocking mode in which `lore-verify` performs read-only / idempotent verification only.
- [REQ-003] Run MUST refuse to execute a test that performs a mutating action against a target marked non-seedable, rather than attempt it and roll back.
- [REQ-004] A destructive or mutating action against a production target MUST require explicit, per-target allowlisting; absent that allowlist, the action MUST be denied.
- [REQ-005] The seedable/mutable declaration and any destructive-action allowlist MUST be recorded in target configuration (LV-ADR-002), not inferred by the agent at run time.
- [REQ-006] When Run blocks an action for prod safety, it MUST report the blocked action clearly so the result is not mistaken for a passing verification.

## Acceptance Criteria

- A test containing a mutating step, run against a target marked non-seedable, is
  refused before execution and reported as blocked, not failed-and-rolled-back.
- A target with no seedable declaration is treated as non-mutable.
- A mutating action runs against production only when that action is explicitly
  allowlisted for that target.

## Success Metrics

- Zero unintended mutations occur against any production target across all runs;
  every prod-mutating action traces to an explicit per-target allowlist entry.

## Risks

- Over-blocking prevents legitimate prod verification. Mitigation: read-only /
  idempotent variants cover most prod checks; the allowlist is the explicit escape
  hatch for the rest.
- A test is mis-classified as read-only when it mutates. Mitigation: fail-closed
  defaults (REQ-001/REQ-002) and explicit allowlisting mean ambiguity denies, not
  permits.

## Assumptions

- Most production verification can be expressed as read-only / idempotent checks.
- Target configuration is a trusted, human-maintained input (it declares
  seedability and allowlists), consistent with the human-review trust boundary
  (RAC ADR-065).

## Related Decisions

- lv-adr-003-runtime-threat-model
- lv-adr-002-pluggable-runner

## Related Requirements

- faithful-session-to-test
- evidence-redaction-and-secret-hygiene

## Related Designs

- runner-interface-and-target-config
