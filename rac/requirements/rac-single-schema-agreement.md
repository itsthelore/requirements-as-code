---
schema_version: 1
id: RAC-KV6KFM5484B9
type: requirement
tags: [internal, schema, contract, mcp, tui]
---
# Requirement: Single-Schema Cross-Consumer Agreement

## Status

Proposed

Classification: `[internal]`. Scoped to the v0.23.0 hardening release (WS6).

## Problem

The artifact schema — front-matter fields, types, relationship kinds, status
enums, required sections — is consumed by the validator, the four MCP tool
serializers, and the TUI. If those consumers could drift apart, a field valid in
one surface might be mis-served in another. RAC already defines the schema once,
in code, as the front-matter envelope (ADR-052, ADR-049); the gap is that no
test *asserts* the consumers still agree, so drift would be silent.

## Requirements

- [REQ-001] The schema MUST remain defined once as the code-defined envelope; this release MUST NOT introduce a parallel schema framework such as a new Pydantic model layer or a JSON-Schema source of truth (ADR-052, ADR-049).
- [REQ-002] The release MUST add a test asserting the validator, the four MCP serializers, and the TUI adapter all agree with the single schema definition for types, statuses, relationship kinds, and required sections.
- [REQ-003] Any residual ad-hoc schema logic found on those consumer paths SHOULD be removed in favor of the single definition.
- [REQ-004] Changing a field in the single definition MUST propagate to every consumer that reads it, demonstrated by the agreement test.

## Acceptance Criteria

- Exactly one schema source exists.
- A test asserts the validator, MCP output, and TUI agree with it.
- Changing a field in one place propagates everywhere it is consumed.

## Success Metrics

- A schema change cannot ship without the agreement test reflecting it across
  all consumers.

## Risks

- The TUI could lag the schema. Mitigation: the TUI already consumes Core via
  `load_repository`, so the agreement test covers it without a migration.

## Assumptions

- The code-defined envelope is, and remains, the authoritative schema (ADR-052).

## Related Decisions

- adr-052
- adr-049
- adr-025

## Related Requirements

- rac-grounding-eval-benchmark

## Related Roadmaps

- v0.23.0-hardening
