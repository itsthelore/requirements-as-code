# Cold-start timing — install to first validated artifact

Measured 2026-06-12 on this machine (Linux, Python 3.11 venv), installing
the local checkout at `/home/user/requirements-as-code` (v0.10.x dev
build, `rac 0.1.dev74`). Wall-clock, `date +%s.%N` around each step.

## Path A: pip in a fresh venv

| Step | Command | Wall clock |
| --- | --- | --- |
| 1 | `python3 -m venv /tmp/coldstart-venv` | 3.43 s |
| 2 | `pip install /home/user/requirements-as-code` | 9.80 s |
| 3 | `rac --version` (sanity check) | 0.13 s |
| 4 | `rac init` | 0.13 s |
| 5 | `mkdir -p rac/requirements` + `rac new requirement rac/requirements/login-flow.md` | 0.15 s |
| 6 | Edit (heredoc replacing TODOs, frontmatter preserved) | 0.01 s |
| 7 | `rac validate rac/requirements/login-flow.md` → PASS, exit 0 | 0.14 s |

Machine total: **≈ 13.8 s**. Result: `PASS`, 0 errors, 1 advisory warning
(`missing-risks`).

## Path B: uv tool install

`uv tool install --force /home/user/requirements-as-code`: **2.57 s**;
`rac --version` works immediately. Zero post-install configuration.

## Verdict

Machine time is ~14 s; the five-minute budget is consumed almost entirely
by human reading and editing. The under-five-minutes cold start
(rac-growth-adoption REQ-002) holds with a wide margin in this
environment.

## Caveats

- Local checkout, not the published PyPI package; a published-package run
  (REQ-003 in `rac/requirements/rac-growth-adoption.md`) should repeat
  this against `pip install requirements-as-code`.
- pip's HTTP cache was warm for dependencies (`markdown-it-py`, `pyyaml`,
  `mcp` and transitive deps); a genuinely cold network adds download time.
  Network conditions should be stated when the published-package run is
  recorded.
- `pipx` is not installed on this machine, so the `pipx install` leg of
  REQ-001 is unverified here; `uv tool install` verified.

## Friction found

- `rac new` does not create parent directories: `rac new requirement
  rac/requirements/login-flow.md` in a fresh project fails with
  `rac: directory does not exist: rac/requirements` until `mkdir -p` is
  run. This is the only zero-config snag on the path; recorded as a gap
  in `.agent-context/gaps/agent2.md` and covered by the Proposed REQ-005
  (guided first-run) in `rac/requirements/rac-growth-adoption.md`.
