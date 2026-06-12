---
schema_version: 1
id: RAC-KTYB6QBZNTD0
type: requirement
---
# RAC Growth — Adoption Surface

## Status

Proposed

## Problem

A new user evaluating RAC has to take its value on trust. The path from
"heard about it" to "first validated artifact on my machine" is not
measured, not demonstrated visually, and depends on the user assembling
the steps themselves from the quickstart. Every extra minute in that path
loses evaluators. The install, first-run, and demonstration surface
should make first value fast, observable, and repeatable.

## Requirements

- [REQ-001] RAC is installable with `pipx install requirements-as-code` and with `uv tool install requirements-as-code`, and the `rac` command works immediately after either install with zero post-install configuration (no config files, environment variables, or accounts required before first use).

- [REQ-002] On a clean machine, a user can go from starting the install to a first artifact passing `rac validate` in under five minutes, using only existing commands: install, then `rac init`, `rac new`, edit the TODO placeholders, `rac validate`.

- [REQ-003] The cold-start path in REQ-002 is timed against a released package version and the measurement recorded in the repository, so the five-minute claim is evidence-backed rather than asserted.

- [REQ-004] The README carries a demo GIF of at most 20 seconds showing the init → author → validate loop (`rac init`, `rac new`, edit, `rac validate`), produced from the shot list in the `growth-demo-gif` design; the GIF complements the existing "90-second demo (link on launch)" placeholder and does not replace it.

- [REQ-005] (Proposed, requires RAC core change) `rac init` offers an optional guided first-run path that scaffolds a `rac/` directory and a first requirement in one step, reducing the cold-start command count; recorded for prioritisation, not implemented as part of this requirement.

## Success Metrics

- Measured cold start (install → first `rac validate` pass) under five
  minutes on a clean environment, recorded with timings.
- Both `pipx` and `uv tool` installs verified to produce a working `rac`
  command with no further configuration.
- README demo GIF present, ≤20 seconds, showing init → author →
  validate.

## Risks

- Install time dominates the five-minute budget on slow networks; the
  measurement should state the network conditions observed.
- The GIF goes stale as CLI output changes; it should be cheap to
  re-record from the shot list.
- `pipx` and `uv` resolve dependencies differently from `pip`; the
  zero-configuration claim must be verified per installer, not assumed.

## Assumptions

- Python 3.11+ is available on the target machine, as `pyproject.toml`
  requires; installing Python itself is outside the five-minute budget.
- The published PyPI package `requirements-as-code` matches the local
  checkout closely enough that local timing is representative.

## Related Requirements

- rac-growth-agent-skill

## Related Designs

- growth-demo-gif
