# Requirement: AI Spec Safety

## Status

Proposed

## Context

AI agents increasingly generate and modify product artifacts such as:

- requirements
- roadmaps
- decisions
- designs
- prompts

These changes can look plausible while quietly weakening product intent.

Examples include:

- replacing measurable requirements with vague language
- removing acceptance criteria
- deleting constraints
- introducing new scope without a linked decision
- breaking relationships between product artifacts
- changing success metrics without review

RAC should provide deterministic safety checks for AI-era product knowledge changes.

## Requirement

RAC shall detect when product artifact changes make product intent less safe, less specific, less connected, or less reviewable.

AI Spec Safety shall focus on the quality and safety of the change, not on proving whether AI authored it.

## Product Goal

Move RAC from:

> Validating Markdown structure.

toward:

> Protecting product intent from unsafe AI-generated or AI-assisted changes.

## User Story

As a team using AI agents to edit product artifacts,

when a requirement, decision, roadmap, or design changes,

I want RAC to identify ambiguity, specificity loss, missing context, and broken relationships,

so that unsafe product intent changes require human review before merge.

## Interfaces

AI Spec Safety shall be consumed through:

```bash
rac guard --base <ref> --head <ref>
```

and structured output:

```bash
rac guard --base <ref> --head <ref> --format json
```

It may also be surfaced through:

- GitHub Actions
- PR comments
- GitHub Checks annotations
- MCP integrations
- Explorer

## Functional Requirements

## Specificity Regression Detection

RAC shall detect when specific, testable language is replaced by vague language.

Example:

```diff
- Payment confirmation must appear within 2 seconds.
+ Payment confirmation should appear quickly.
```

RAC reports:

```text
Specificity regression detected.

"within 2 seconds" was replaced by "quickly".

The requirement is no longer objectively testable.
```

## Ambiguity Detection

RAC shall flag ambiguous language when unsupported by measurable criteria.

Examples:

- fast
- easy
- seamless
- intuitive
- scalable
- user-friendly
- robust
- simple

Example:

```text
REQ-004 contains ambiguous language:

"Checkout should be fast."

Issue:
"fast" is not measurable without a target.
```

## Constraint Removal Detection

RAC shall detect removed or weakened constraints.

Examples:

```diff
- Must support WCAG 2.2 AA.
+ Should be accessible.
```

```diff
- The API must reject duplicate payment attempts.
+ The API should handle duplicate payment attempts.
```

## Acceptance Criteria Regression

RAC shall detect when acceptance criteria are removed, weakened, or made less testable.

Examples:

- deleting acceptance criteria
- changing `must` to `should`
- replacing numeric thresholds with subjective wording
- removing edge cases

## Metric Regression Detection

RAC shall detect when success metrics are removed or weakened.

Example:

```diff
- Upgrade completion rate must reach 95%.
+ Upgrade completion should be high.
```

RAC reports:

```text
Metric regression detected.

"95%" was replaced by "high".
```

## Scope Expansion Detection

RAC shall detect when new product scope is introduced without supporting context.

Examples:

- new requirement without linked roadmap outcome
- new dependency without linked decision
- new design behavior without linked requirement
- new prompt behavior without linked requirement or decision

## Relationship Safety

RAC shall detect whether product changes break or weaken artifact relationships.

Examples:

- deleted linked artifacts
- broken references
- ambiguous relationship targets
- orphaned requirements
- decisions superseding missing decisions

## Human Review Recommendation

RAC shall recommend whether product-owner review is required.

Example outcomes:

```text
PASS

No unsafe product intent changes detected.
```

```text
WARN

Review recommended:
2 ambiguous requirements introduced.
```

```text
BLOCK

Human product review required:
Acceptance criteria removed from REQ-004.
```

## Non-Goals

AI Spec Safety shall not:

- prove whether content was AI-generated
- classify authorship
- replace human product judgment
- decide whether a product decision is correct
- rewrite artifacts automatically
- require a hosted AI service

The safety concern is not who wrote the change.

The concern is whether the change made product intent less safe.

## Architecture Requirements

AI Spec Safety shall be implemented as RAC core intelligence.

Consumers shall follow:

```text
Core Safety Analysis
        |
        |
     rac guard
        |
        |
 JSON / GitHub / MCP / Explorer
```

No GitHub integration, MCP layer, or Explorer surface shall independently implement safety logic.

## Acceptance Criteria

RAC can compare two product artifact states and report:

- ambiguity introduced
- specificity removed
- constraints removed
- metrics weakened
- acceptance criteria weakened
- relationships broken
- scope introduced without context
- recommended review action

## Success Measures

AI Spec Safety succeeds when:

- AI-generated product changes become reviewable.
- product intent regressions are caught before merge.
- teams can safely use agents to modify requirements.
- CI identifies unsafe product knowledge changes.
- product owners review high-risk changes intentionally.

## Related Artifacts

- Requirement: Repository Review Mode
- Requirement: Product Intent CI
- ADR: Markdown First
- ADR: Repository Intelligence as the Value Layer
- ADR: Explorer as a Consumer

## Future Considerations

Future iterations may support:

- organization-specific ambiguity dictionaries
- custom safety policies
- agent provenance metadata
- product-owner approval workflows
- historical intent drift tracking
- MCP-native safety checks
```