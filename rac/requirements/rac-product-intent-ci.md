# Requirement: Product Intent CI

## Status

Proposed

## Context

Software engineering workflows protect code changes through automated quality gates:

- tests
- linting
- formatting
- static analysis
- security checks
- dependency checks

Product knowledge rarely receives equivalent protection.

Requirements, decisions, roadmaps, designs, and prompts are often modified without automated verification.

This risk increases as AI coding agents begin generating and modifying product intent directly.

A change can appear correct while silently introducing:

- invalid requirements
- ambiguous language
- broken relationships
- missing decisions
- removed acceptance criteria
- unintended scope changes

RAC should provide the missing CI layer for product knowledge.

## Requirement

RAC shall provide CI-native verification of product intent changes before they are merged.

Teams should be able to install RAC once and continuously verify product artifacts through their existing development workflow.

## Product Goal

Move RAC from:

> A CLI toolkit for Markdown product artifacts.

toward:

> CI for product intent.

## User Story

As a team storing product knowledge in Git,

when humans or AI agents modify product artifacts,

I want automated checks before merge,

so that unsafe product changes are caught before they reach engineering.

## Dependency

Product Intent CI depends on:

- Repository Review Mode for repository health analysis.
- AI Spec Safety for intent-change analysis.
- RAC diff capabilities for artifact change detection.

This requirement defines where product checks execute.

It does not redefine the checks themselves.

## User Workflow

A user installs RAC:

```bash
uv tool install requirements-as-code
```

Then initializes a repository:

```bash
rac init
```

RAC creates:

```text
rac/
  requirements/
  decisions/
  roadmaps/
  designs/
  prompts/

.github/
  workflows/
    rac.yml
```

The generated workflow enables automatic product intent checks on pull requests.

## Primary Interface

Product Intent CI shall expose a single command:

```bash
rac guard
```

Optional:

```bash
rac guard --base main --head HEAD

rac guard --format json

rac guard --format github
```

Users should not need to manually compose lower-level RAC commands.

Internally:

```text
rac guard
     |
     +-- Repository Review
     |
     +-- Artifact Diff
     |
     +-- AI Spec Safety
```

## Functional Requirements

## GitHub Action Integration

RAC shall provide a standard GitHub Actions workflow.

Example:

```yaml
name: RAC Product Intent Check

on:
  pull_request:

jobs:
  rac:
    steps:
      - run: rac guard --format github
```

The workflow shall support:

- installing RAC
- detecting changed product artifacts
- executing product safety checks
- reporting results to pull requests

## Pull Request Safety Gate

RAC shall determine whether a product change is safe to merge.

Example:

```text
RAC Guard

Status:
Review Required

Changed:

+ 3 Requirements
~ 2 Decisions

Issues:

BLOCK:
- REQ-004 missing Acceptance Criteria
- ADR-007 references missing ADR-002

WARN:
- ROADMAP-Q3 missing Success Measures
```

## Product Knowledge Diff

RAC shall summarize product-level changes.

The output should explain intent changes, not raw Markdown changes.

Example:

```text
This PR:

Added:
+ Billing upgrade requirement

Modified:
~ Checkout decision

Removed:
- Legacy payment constraint

Impact:

1 downstream roadmap affected
```

## Configurable Quality Gates

Teams shall configure which issues:

- block merges
- require review
- generate warnings

Example:

```yaml
guard:
  fail_on:
    - invalid_artifact
    - broken_relationship
    - duplicate_identifier

  require_review:
    - acceptance_criteria_removed
    - scope_added
    - ambiguity_introduced

  warn_on:
    - missing_recommended_section
```

## GitHub Review Output

RAC shall provide human-readable pull request feedback.

Example:

```text
RAC Product Intent Report

4 artifacts changed.

✓ Structure valid
✓ Relationships valid

⚠ Human review recommended

Reasons:

- 2 requirements became less specific
- 1 new dependency added without Decision
```

## GitHub Check Annotations

RAC should support native review annotations.

Example:

```text
requirements/payment.md

"Payment should complete quickly"

Issue:
"quickly" is ambiguous.

Recommendation:
Use measurable criteria.
```

## Product Ownership Rules

RAC may support ownership policies for product knowledge.

Example:

```yaml
ownership:
  requirements/billing/*:
    reviewers:
      - billing-owner
```

Changes affecting owned areas may require explicit review.

## Machine Readable Contract

All CI integrations shall consume structured RAC output.

Required:

```bash
rac guard --format json
```

Consumers include:

- GitHub Actions
- CI providers
- MCP servers
- AI agents
- Explorer

## Non-Goals

Product Intent CI shall not:

- replace human product ownership
- determine whether product strategy is correct
- rewrite requirements automatically
- require GitHub specifically
- require hosted infrastructure
- duplicate RAC analysis logic

## Architecture Requirements

Product Intent CI shall follow:

```text
Core RAC Intelligence
          |
          |
     rac guard
          |
          |
 JSON / GitHub Output
          |
          |
 CI / Agents / Explorer
```

GitHub Actions are consumers of RAC intelligence.

They are not the source of product intelligence.

## Acceptance Criteria

A team can:

1. Install RAC.
2. Run `rac init`.
3. Open a pull request modifying product artifacts.
4. Automatically receive:
   - repository health results
   - artifact change summary
   - relationship validation
   - intent safety findings
   - merge recommendation

without manually running RAC commands.

## Success Measures

Product Intent CI succeeds when:

- product changes receive automated review like code changes
- AI-generated specification changes become safer
- unsafe requirement changes are detected before implementation
- teams trust agents to modify product artifacts with guardrails
- product knowledge becomes continuously verified

## Related Artifacts

- Requirement: Repository Review Mode
- Requirement: AI Spec Safety
- ADR: Markdown First
- ADR: Repository Intelligence as the Value Layer
- ADR: Explorer as a Consumer

## Future Considerations

Future versions may support:

- additional CI providers
- advanced ownership workflows
- product approval rules
- product impact graphs
- release intent summaries
- historical drift detection
- organization policy packs
```