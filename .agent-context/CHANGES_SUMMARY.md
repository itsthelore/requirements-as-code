# Growth programme — changes summary

Branch `claude/rac-growth-orchestration-obphpo`, 2026-06-12. The
programme was adapted before execution: ADR-036 (Lore product identity)
governs positioning, so the layer-above-SDD thesis appears only as
comparison content below the README fold; the dogfood-conversion
workstream was re-scoped to a corpus gap audit because the corpus is
already fully RAC-native; gap records motivate future roadmap work, not
"v0.8.0". Adaptation confirmed by the maintainer on 2026-06-12.

## Agent 1 — positioning and comparison

Authored `rac-growth-positioning` (REQ-001..005), then satisfied it
with one README section, "How this relates to spec-driven development",
inserted below "Who it's for": layer-above thesis, a five-dimension
comparison table against GitHub Spec Kit and OpenSpec, every cell
verified against the tools' own repos with sources in an adjacent HTML
comment. Kiro is named in prose only — its docs returned HTTP 403 at
verification time, so no Kiro capability claims are made. First screen
byte-identical; pure 36-line insertion.

## Agent 2 — adoption surface

Authored `rac-growth-adoption` (REQ-001..005: pipx/uv zero-config
install, sub-five-minute cold start, timing evidence, ≤20 s demo GIF;
REQ-005 is the one item needing a core change, left Proposed) and
`rac-growth-agent-skill` (REQ-001..004). Implemented the Claude Code
skill at `.claude/skills/rac-artifacts/SKILL.md` per Anthropic's
documented project discovery path, constrained to the host project's
RAC directory. Measured cold start: ≈13.8 s machine time
(`.agent-context/cold-start-timing.md`). Demo shot list recorded as the
`growth-demo-gif` design (5 shots, 20 s).

## Agent 3 — gap audit and contribution policy (re-scoped)

Audited the existing corpus and recorded seven traceability gaps with
3–4 concrete instances each (`.agent-context/gaps/agent3.md`). Authored
`rac-growth-contribution-policy` (REQ-001..005): proposal-gated
substantial changes modelled on OpenSpec's verified flow, draft
CONTRIBUTING.md text embedded in the artifact body, the live file
untouched, marked Blocked: GATE-2.

## Agent 4 — essay–artifact bridge

Authored `rac-growth-essay-bridge` (REQ-001..004, Blocked: GATE-1) and
the `growth-essay-mapping` design: six Article 1 claims mapped to
verified capabilities or explicitly flagged absences, least-promotional
link placements, and five dogfood article slots (titles and one-line
premises only). Zero prose written in the maintainer's voice.

## Agent 5 — ecosystem seed

Authored `rac-growth-extensibility` (REQ-001..005: entry-point
discovery of third-party schemas/templates, byte-identical behaviour
when absent, designed within ADR-012/015/021/024; GATE-2-blocked
standalone-repo bundle convention draft embedded) and
`rac-growth-ecosystem-list` (REQ-001..005). Created `docs/ecosystem.md`
with exactly three verified entries (dogfood corpus, the
`rac-artifacts` skill, `examples/guide/`) and no solicitation language.

## Requirement artifacts created

| Artifact | Id | REQs | Status |
| --- | --- | --- | --- |
| rac/requirements/rac-growth-positioning.md | RAC-KTYB8944G7TN | REQ-001..005 | Proposed |
| rac/requirements/rac-growth-adoption.md | RAC-KTYB6QBZNTD0 | REQ-001..005 | Proposed |
| rac/requirements/rac-growth-agent-skill.md | RAC-KTYB6R0DM280 | REQ-001..004 | Proposed |
| rac/requirements/rac-growth-contribution-policy.md | RAC-KTYBCCTFG5JW | REQ-001..005 | Proposed, Blocked: GATE-2 |
| rac/requirements/rac-growth-essay-bridge.md | RAC-KTYBHXKBWZGZ | REQ-001..004 | Proposed, Blocked: GATE-1 |
| rac/requirements/rac-growth-extensibility.md | RAC-KTYBK6T1NQMY | REQ-001..005 | Proposed (bundle section GATE-2) |
| rac/requirements/rac-growth-ecosystem-list.md | RAC-KTYBK7FSW6HS | REQ-001..005 | Proposed |

Supporting corpus artifacts: `rac/roadmaps/future/growth-programme.md`
(RAC-KTYB8RVVQ1HX, umbrella, links all of the above),
`rac/designs/growth-demo-gif.md` (RAC-KTYB6RMYBQ5X),
`rac/designs/growth-essay-mapping.md` (RAC-KTYBHY87XKV8).

Non-corpus artifacts: README comparison section,
`.claude/skills/rac-artifacts/SKILL.md`, `docs/ecosystem.md`,
`.agent-context/` (brief, schema, timing log, five gap files, this
summary, `GAPS_TRACEABILITY.md`).

## Integration review results

- `rac validate rac/`: 113 valid, 0 invalid, exit 0.
- `rac relationships rac/ --validate`: 277 checked, 0 issues, exit 0.
- `rac review rac/`: health 80/100, zero priority 1–2 findings.
- Every produced artifact traces to a requirement (recorded in prose —
  the structural link is itself gap 1 of `GAPS_TRACEABILITY.md`).
- All competitor claims source-cited; the OpenSpec packaging quote and
  contribution-model claims were independently re-verified against the
  live README at integration. No uncited claim survived.
- Gate check: `Blocked: GATE-1/GATE-2` markers present on all four
  gated artifacts; grep confirms no gate-blocked content in README,
  docs/, examples/, or the skill.
