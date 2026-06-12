---
schema_version: 1
id: RAC-KTYXDP8HSVS5
type: requirement
---
# REQ-Docs-Site-Landing-Page

## Status

Proposed

## Problem

Lore has no marketing-grade entry point. A prospective user evaluating the
product today lands on a 163-line README rendered by GitHub — there is no
page that presents the hero art, the value proposition, the install command,
and a path into the documentation in one screen. The approved scoping design
(`docs-site-scoping`) defines a landing page modelled on openspec.dev's
structure (hero → what it is → install → links into docs) as the site's
front door; this artifact governs that page.

## Requirements

- [REQ-001] The site MUST serve a landing page at the site root, sourced from `docs/index.md`.

- [REQ-002] The landing page MUST render the Lore header art with light and dark variants served from `docs/images/lore-header-light.png` and `docs/images/lore-header-dark.png`, switching with the active Material color scheme, and MUST carry the existing alt text ("Lore — agents that know why. Deterministic. Read-only. No RAG, no guessing.").

- [REQ-003] The hero headline MUST be the existing tagline verbatim: "Give your coding agent the decisions your team already made — so it stops re-doing things you ruled out."

- [REQ-004] The landing page MUST render the hero image, the install command `pip install requirements-as-code` in a copyable code block, and three documentation links (Quickstart, MCP Server, CLI Reference) above the fold at a 1280×800 desktop viewport.

- [REQ-005] The install section SHOULD state the `uv tool install` alternative and the Python 3.11+ requirement.

- [REQ-006] The page MUST include a "what it is" section containing the agent-grounding value proposition and the Lore-product / RAC-engine naming, relocated verbatim from the README.

- [REQ-007] Below the fold, the page MUST contain, in this order: "Why this works"; the spec-driven-development positioning paragraph with the Lore / GitHub Spec Kit / OpenSpec comparison table and its sources comment; "How Lore earns trust"; and footer links (GitHub repository, project status one-liner, CONTRIBUTING, MIT license) — each relocated verbatim from the README.

- [REQ-008] The page MUST be built with stock Material theme capabilities; custom HTML/CSS MAY be used only where a requirement in this artifact is unreachable without it, and any such code MUST be confined to a single override file.

## Acceptance Criteria

- At a 1280×800 viewport, the hero image, the install command, and the
  three documentation links are visible without scrolling (verified with a
  rendered-page screenshot recorded in the implementation PR).
- Toggling the Material color scheme switches the header art between the
  light and dark variants.
- The page's section order matches REQ-004 then REQ-006 then REQ-007
  exactly; no sections beyond those listed are present.
- A diff of each relocated section against its README source shows no prose
  changes (formatting adjustments for MkDocs rendering excepted).
- The repository contains at most one theme-override file, and only if at
  least one requirement above is demonstrably unreachable without it.
- `mkdocs build --strict` exits 0 with `docs/index.md` mapped to the Home
  nav position.

## Success Metrics

- A reader at the site root can identify what Lore is, see the install
  command, and reach the Quickstart in one click without scrolling.
- The landing page introduces zero new prose: every sentence is traceable
  to the README or the scoping design's wireframe.

## Risks

- The header art was designed for the README's width; it may need width
  constraints (not edits) to sit correctly in Material's content column.
- "Above the fold" depends on browser chrome; the 1280×800 viewport pins
  the testable definition.

## Assumptions

- The header art files in `rac/assets/images/` are current brand assets and
  may be copied into `docs/images/` unchanged.
- The README's tagline and value-proposition copy remain stable while this
  work is in flight; if the README changes first, the relocated copy
  follows the README at implementation time.

## Related Requirements

- rac-docs-site-platform
- rac-docs-site-readme-doorway

## Related Decisions

- ADR-036
- ADR-042

## Related Designs

- docs-site-scoping

## Related Roadmaps

- v0.10.7-docs-site
