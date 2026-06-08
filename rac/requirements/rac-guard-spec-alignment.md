# Requirement: AI Spec Safety Review

## Status

Proposed

## Context

AI coding agents increasingly create and modify product artifacts before implementation.

Agents can now:

- generate requirements
- update roadmaps
- modify design decisions
- rewrite acceptance criteria
- restructure planning documents

However, product knowledge currently lacks the automated safeguards available for source code.

Code has:

- tests
- type checking
- linting
- static analysis
- CI gates

Product intent often relies on manual review.

AI-generated changes can appear correct while silently introducing:

- ambiguity
- scope changes
- missing constraints
- weakened acceptance criteria
- broken relationships
- disconnected decisions

RAC exists to provide deterministic safety checks around changing product knowledge.

## Requirement

RAC shall provide an AI Spec Safety workflow that reviews product intent changes before they are merged.

Given two repository states, RAC shall identify:

- what product meaning changed
- what became ambiguous
- what became invalid
- what became disconnected
- what requires human review

## Product Goal

Move RAC from:

> A validator for Markdown artifacts.

toward:

> The CI safety layer for AI-generated product changes.

## User Story

As a team using AI coding agents,

when an agent modifies product artifacts,

I want RAC to review the product intent change before merge,

so that AI-generated changes cannot silently weaken requirements, remove constraints, or disconnect decisions.

## Example Workflow

A developer or agent opens a pull request.

RAC runs:

```bash
rac guard --base main --head HEAD
```

or through CI:

```yaml
- name: RAC Product Intent Safety
  run: rac guard --base origin/main --head HEAD --format github
```

RAC reports:

```text
RAC AI Spec Safety Report

Changed product intent:

requirements/billing-upgrade.md

Added:
+ 3 Requirements

Removed:
- Constraint requiring upgrade confirmation within 2 seconds

Changed:
- "95% upgrade completion"
+ "high upgrade completion"

Risk:
Specific measurable success criteria replaced with ambiguous wording.

Relationship issues:

- Added dependency on Stripe webhooks
- No linked Decision artifact found

Recommendation:

Require product owner review before merge.
```

## Functional Requirements

## Product Intent Diff

RAC shall identify meaningful artifact changes.

Examples:

- requirements added
- requirements removed
- acceptance criteria changed
- constraints modified
- metrics changed
- risks removed
- decisions changed

The output should summarize product impact, not raw text differences.

## Specificity Regression Detection

RAC shall identify when precise requirements become ambiguous.

Example:

Before:

```text
Payment confirmation must appear within 2 seconds.
```

After:

```text
Payment confirmation should appear quickly.
```

RAC reports:

```text
Specificity regression detected.

"within 2 seconds" changed to "quickly".

Requirement is no longer objectively testable.
```

## Ambiguity Detection

RAC shall detect unclear product language.

Examples:

- fast
- easy
- seamless
- intuitive
- scalable
- user-friendly

without supporting measurable criteria.

Example:

```text
REQ-004:

"Checkout should be fast"

Issue:
"fast" has no measurable success criteria.
```

## Relationship Safety

RAC shall detect:

- deleted linked artifacts
- broken references
- ambiguous relationship targets
- new scope without decisions
- orphaned requirements

Example:

```text
ROADMAP-002 references REQ-010.

REQ-010 was removed in this change.
```

## Scope Change Detection

RAC shall identify when new product scope appears without supporting context.

Examples:

- requirement added without roadmap relationship
- technical dependency added without decision
- design constraint changed without explanation

## Review Recommendation

RAC shall produce a merge recommendation.

Examples:

```text
PASS

Product intent unchanged.
```

```text
WARN

Review recommended:
2 ambiguity issues introduced.
```

```text
BLOCK

Human product review required:
Requirement removed without replacement.
```

## Interfaces

### CLI

Required:

```bash
rac guard --base <ref> --head <ref>
```

Optional:

```bash
rac guard --changed-only
rac guard --format json
rac guard --format github
```

## GitHub Integration

RAC Guard shall support PR comments.

Example:

```text
RAC Product Safety

4 artifacts changed

✓ Structure valid
✓ Relationships valid

⚠ Human review recommended

Reasons:
- 2 ambiguous requirements introduced
- 1 metric removed
```

## JSON Contract

All safety information shall be available through structured output.

Consumers include:

- GitHub Actions
- MCP servers
- AI agents
- Explorer

## Non-Goals

RAC Guard shall not:

- determine whether a product decision is correct
- replace product owners
- automatically rewrite requirements
- require AI-generated content detection
- rely on probabilistic authorship guessing

The concern is not whether AI wrote the change.

The concern is whether the change made product knowledge less safe.

## Architecture Requirements

Implementation order:

```text
Core diff intelligence
        ↓
Safety analysis service
        ↓
CLI command
        ↓
JSON output
        ↓
GitHub / MCP / Explorer
```

All consumers must use the same RAC intelligence layer.

## Acceptance Criteria

A pull request changing product artifacts can report:

- artifacts changed
- intent changes
- validation regressions
- relationship regressions
- ambiguity introduced
- specificity removed
- required human review

without manually inspecting Markdown diffs.

## Success Measures

RAC succeeds when:

- AI-generated requirement changes become reviewable.
- Product knowledge receives CI-level safety checks.
- Teams catch intent drift before engineering begins.
- Agents can modify specs without removing accountability.
- Product changes become as inspectable as code changes.

## Related Artifacts

- Requirement: Repository Review Mode
- Requirement: Product Knowledge Pull Request Review
- ADR: Markdown First
- ADR: Repository Intelligence as the Value Layer
- ADR: Explorer as a Consumer

## Future Considerations

Future versions may add:

- agent attribution metadata
- MCP integration
- organization-specific safety policies
- approval workflows
- historical intent drift tracking
- product knowledge coverage reports
```