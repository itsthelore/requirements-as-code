# Traceability gaps — consolidated report

Growth programme, 2026-06-12, corpus at v0.10.3. Twenty raw gap records
from five agents (`.agent-context/gaps/agent1..5.md`) consolidate into
eight schema gaps and two authoring-friction findings. Every instance
cites a real file in this repository; none is speculative. The original
programme framed this report as justification for "the v0.8.0
traceability work"; that shipped as the v0.7.x relationships series
(ADR-016), so each gap instead names the future work it motivates.

The linking mechanisms that exist today: untyped `## Related <Type>`
sections (corpus-internal, by id) and `## Supersedes` (decisions only).

## 1. Links from artifacts to non-artifact repo files

The most frequently hit gap — all five agents recorded it independently.

- Instances: `rac-growth-positioning` REQ-001..005 are satisfied by a
  README section it cannot reference; `rac-growth-agent-skill` REQ-001
  is satisfied by `.claude/skills/rac-artifacts/SKILL.md`;
  `rac-growth-ecosystem-list` governs `docs/ecosystem.md`; pre-existing:
  `rac-documentation-structure` places testable requirements on eight
  doc files by bare path, and `adr-027` governs four CI workflow files
  the same way. Renames break these silently.
- Minimal addition: an optional `## Related Files` (or `## Satisfied
  By`) section accepting repo-relative paths, validated for existence
  by `rac relationships --validate`.
- Motivates: requirement→artifact traceability in a future
  relationships milestone; also gives Guide's `get_related` a way to
  answer "what file satisfies this requirement".

## 2. External source and URL references as structured data

- Instances: the README comparison table's competitor sources
  (spec-kit, OpenSpec) live in an HTML comment invisible to validation
  and MCP; Kiro's exclusion (docs returned HTTP 403 on 2026-06-12)
  has no machine-readable "re-verify later" marker; the essay series
  mapped in `growth-essay-mapping` is unpublished and external, so the
  article side of every mapping row is an unresolvable label.
- Minimal addition: an optional `## Sources` section, one URL per line
  with an optional status token, extracted and exposed via
  `get_artifact` (not fetched by the engine — determinism holds).
- Motivates: evidence-grounded artifacts; staleness checking as a
  deterministic review finding.

## 3. Typed edge semantics (implements / satisfies / depends-on / derived-from)

- Instances: `adr-028` invents unvalidated `### Implements`
  sub-headings inside a non-schema section; the Explorer requirement
  invents `### Depends On`; `v0.10.3-search-quality` lists the
  decisions it implements (ADR-037/038) and the standing constraints it
  must not break (ADR-007/027) in one flat `## Related Decisions` list;
  `growth-essay-mapping`'s claim→capability mapping is unqueryable
  table prose.
- Minimal addition: validated optional edge-label sub-headings
  (`### Implements`, `### Depends On`, `### Satisfies`) inside existing
  `Related <Type>` sections, defaulting to untyped when absent.
- Motivates: relationship semantics in a post-v0.10 series; directly
  improves `rac relationships` output and `get_related` answer quality.

## 4. Machine-readable lifecycle and gate status

- Instances: `rac-product-intent-ci-watchkeeper` carries Status
  "Deferred", outside any vocabulary, accepted silently; shipped
  requirements still read "Proposed" with no transition to record;
  this programme's GATE-1/GATE-2 markers are free-text lines
  (`Blocked: GATE-2 (CLA not yet in place)`) in four artifacts —
  nothing can enumerate "everything blocked behind GATE-1", and the
  section-level block on `rac-growth-extensibility`'s bundle convention
  is pure prose.
- Minimal addition: a validated Status vocabulary for requirements
  (Proposed | Accepted | Implemented | Deferred | Blocked) with one
  reason line for Blocked.
- Motivates: the review engine (`future/v1.1-review-engine`) and CI
  Watchkeeper intent analysis, both of which need lifecycle state.

## 5. Supersession outside decisions

- Instances: `archive/v0.8.0-service-api.md` and
  `v0.8.x-explorer/v0.8.0-explorer-foundation.md` both claim the v0.8.0
  identity with no marker between them; the entire archived v0.9 plan
  was replaced by `v0.9.x-watchekeeper/` via directory move only;
  `v0.10.0-guide-foundation` supersedes the deleted `v1.2-mcp-server`
  stub in prose that now dangles invisibly.
- Minimal addition: permit `## Supersedes` on roadmap artifacts,
  validated for target existence including archived targets.
- Motivates: roadmap lifecycle hygiene; makes `archive/` queryable
  instead of conventional.

## 6. Relationship directionality and back-references

- Instances: ADR-036 → v0.10.2 has no reverse edge; six early ADRs
  cited by `rac-agent-context-guide` carry zero Related sections
  themselves — an agent at the target cannot discover the citing
  artifact.
- Minimal addition: an advisory asymmetric-edge finding in
  `rac relationships --validate` (no schema change).
- Motivates: relationship-quality findings in the review engine.

## 7. Scoping / applies-to

- Instances: ADR-018 governs `rac/`; ADR-023 scopes itself to
  `src/rac/` internals in bold prose; ADR-027 applies to the CI
  workflows; ADR-033 applies to the Guide tool surface — none of these
  scopes is data.
- Minimal addition: an optional `## Applies To` section on decisions
  accepting paths or component names.
- Motivates: scoped grounding — Guide could serve "decisions that apply
  to the file you are editing".

## 8. Validation blind spots in relationship extraction

- Instances: `## Related Artifacts` (a non-schema section) appears in
  eight artifacts with display-name targets that resolve to nothing
  while CI stays green; `rac-growth-agent-skill` links
  `v1.4-claude-skills`, whose file classifies as Unknown type, and
  validation reports 0 issues — targets are not type-checked.
- Minimal addition: advisory findings for unrecognised `Related *`
  sections and for targets resolving to Unknown or mismatched types.
- Motivates: near-term `rac review` / relationships hardening; cheap
  relative to the schema gaps above.

## Authoring-friction findings (not schema gaps)

- `[REQ-NNN]` statements cannot hard-wrap: continuation lines raise
  `req-missing-id`, forcing one-line statements against the corpus's
  72-column prose convention. Hit by three agents.
- `rac new` does not create parent directories — the only zero-config
  snag on the measured cold-start path (covered by Proposed REQ-005 in
  `rac-growth-adoption`).
