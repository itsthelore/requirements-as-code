# Agent 5 (ecosystem seed) — schema gaps

## Gap: link from an artifact to a non-artifact file

- Instance: `rac-growth-ecosystem-list` governs `docs/ecosystem.md` but
  the only linking mechanism is `## Related <Type>` by corpus-internal
  id; the requirement cannot reference the page it specifies, so the
  trace exists only as prose in REQ-001.
- Instance: `rac-growth-extensibility` is about the registry in
  `src/rac/core/artifacts.py` and the templates under
  `src/rac/templates/`, neither of which can be a relationship target.
- Minimal schema addition that would have sufficed: a `## Related
  Files` optional section accepting repository-relative paths,
  extracted but validated only for existence.

## Gap: reference to an external repository (ecosystem entry)

- Instance: the draft third-party bundle convention in
  `rac-growth-extensibility` anticipates bundles living in standalone
  repositories; once one exists there is no way to record it in the
  corpus — an ecosystem entry's external repo is representable only as
  a Markdown link in `docs/ecosystem.md`, outside validation entirely.
- Minimal schema addition that would have sufficed: allow a `## Related
  <Type>` line to carry a URL alongside the id (or a `## Related
  External` section of bare URLs), extracted as metadata without
  resolution.

## Gap: machine-readable gate/blocked status on part of an artifact

- Instance: the bundle convention draft is GATE-2-blocked while the
  rest of `rac-growth-extensibility` is an ordinary Proposed
  requirement; the brief's marking convention (`Blocked: ...` body
  line) covers whole artifacts, so a section-level block is a prose
  line under the section heading that no tool can query or enforce.
- Minimal schema addition that would have sufficed: a validated
  `Blocked` metadata value (artifact-level would cover most cases) in
  the requirement `## Status` vocabulary, so gated content is
  discoverable by query rather than by reading.
