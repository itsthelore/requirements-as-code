# Gaps — agent 2 (adoption surface)

## Gap: link from a requirement to the non-artifact file that satisfies it
- Instance: `rac-growth-agent-skill` REQ-001 is satisfied by
  `.claude/skills/rac-artifacts/SKILL.md`; no `## Related …` section can
  reference a file outside the corpus, so the requirement names the path
  in prose only.
- Instance: `rac-growth-adoption` REQ-003's evidence is the timing
  record (`.agent-context/cold-start-timing.md` now; a published-package
  run later); there is no way to attach evidence to a requirement.
- Instance: `rac-growth-adoption` REQ-004's deliverable is a README
  asset (the demo GIF); the requirement cannot reference the README or
  the asset path.
- Minimal schema addition that would have sufficed: an optional
  `## Related Files` section accepting repo-relative paths, with
  existence checked by `rac relationships --validate`.

## Gap: relationship targets are not type-checked
- Instance: `rac-growth-agent-skill` lists `v1.4-claude-skills` under
  `## Related Roadmaps`; that file (`rac/roadmaps/future/v1.4-claude-skills.md`)
  is a stub that classifies as Unknown (its body says "1.3 Claude
  Skills"), yet `rac relationships rac/ --validate` reports 0 issues.
- Minimal schema addition that would have sufficed: a warning from
  relationship validation when a `## Related <Type>` target resolves to
  an artifact of a different or unknown type.

## Gap: requirement statements cannot be hard-wrapped
- Instance: both new requirements initially wrapped `[REQ-NNN]` bullets
  at ~72 columns, the corpus's prose convention; every continuation line
  raised `req-missing-id`, forcing each statement onto one long line.
- Minimal schema addition that would have sufficed: treat indented
  continuation lines of a `[REQ-NNN]` bullet as part of that
  requirement during validation.

## Gap: `rac new` does not create parent directories (CLI capability)
- Instance: cold-start run — in a fresh project after `rac init`,
  `rac new requirement rac/requirements/login-flow.md` fails with
  `rac: directory does not exist: rac/requirements` until `mkdir -p` is
  run; the only zero-config snag on the first-value path (see
  `.agent-context/cold-start-timing.md`; covered by Proposed REQ-005 in
  `rac-growth-adoption`).
- Minimal schema addition that would have sufficed: not schema —
  `rac new` creating missing parent directories of the output path
  would have sufficed.
