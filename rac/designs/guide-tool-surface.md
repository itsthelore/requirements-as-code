---
schema_version: 1
id: RAC-KTW0M82QMVBF
type: design
---
# Guide Tool Surface

## Context

RAC Guide serves repository knowledge to coding agents over MCP.

Guide has no screen. Its entire user experience is four tool definitions: the
names, signatures, and description text an agent reads when deciding whether
to call. Tool descriptions are to Guide what the visual system is to
Explorer — the product surface itself.

The descriptions therefore carry the grounding behaviour. An agent that never
calls `search_artifacts` before implementing never sees the decision it is
about to violate. Triggering at the right moment is a design outcome, not an
implementation detail.

Response shapes are equally part of the surface: they land in the agent's
context window and are pinned contracts (ADR-007, ADR-030, ADR-033).

## User Need

An agent mid-task needs the right artifact at the right moment without being
told to look:

- before implementing, the decisions and requirements that constrain the work
- when an artifact ID appears, the artifact behind it
- after retrieving an artifact, what connects to it
- at session start, what recorded knowledge exists at all

The agent chooses tools by description alone. The description must make the
"when" unmistakable.

## Design

Four read-only tools. Names, signatures, and description text below are
pinned verbatim; implementation must ship them unchanged, and changing them
is a contract change.

All responses are JSON objects with `"schema_version": "1"`. Output is
deterministic: identical repository state and identical input produce
identical output (ADR-032), with stable ordering throughout.

### get_artifact

Signature:

```text
get_artifact(id: str)
```

Description (verbatim):

> Retrieve one artifact from this repository's recorded product knowledge —
> a requirement, decision (ADR), design, roadmap, or prompt — by its
> identifier. Call this whenever an artifact ID is mentioned (for example
> REQ-001, ADR-012, or a RAC-prefixed ID), and before relying on or changing
> anything a known requirement or decision covers. Returns the artifact's
> metadata and full Markdown content.

Resolution uses the exact semantics of `rac resolve`: three outcomes —
resolved, not found, duplicate — and a duplicate is never silently resolved.

Resolved response:

```json
{
  "schema_version": "1",
  "id": "...",
  "type": "...",
  "title": "...",
  "path": "...",
  "content": "..."
}
```

`id`, `type`, `title`, and `path` are the resolver's answer
(`ResolutionResult`). `content` is added by the server layer: the artifact
file's text exactly as stored, frontmatter included.

### search_artifacts

Signature:

```text
search_artifacts(query: str, type: str | None = None)
```

Description (verbatim):

> Search this repository's recorded product knowledge — requirements,
> decisions (ADRs), designs, roadmaps, and prompts — by keyword. Call this
> before designing or implementing anything that an existing requirement or
> prior decision might cover, and whenever the user mentions a feature area,
> so recorded decisions are respected instead of rediscovered. Returns
> matching artifact IDs, types, titles, and paths; use get_artifact to read
> a match.

Search uses the exact semantics of `rac find`: case-insensitive substring
matching over identifiers, title, and path, ordered by match-field priority
with sorted path as tiebreak. v1 adds no semantics beyond what
`find_artifacts` does today.

Response (`SearchResult.to_dict`):

```json
{
  "schema_version": "1",
  "query": "...",
  "type": null,
  "match_count": 0,
  "matches": [
    {"id": "...", "type": "...", "title": "...", "path": "..."}
  ]
}
```

### get_related

Signature:

```text
get_related(id: str)
```

Description (verbatim):

> List the artifacts connected to one artifact in this repository's product
> knowledge: the references it declares and the artifacts that reference
> it. Call this after retrieving an artifact, and before changing anything
> it covers, to find the decisions, requirements, designs, and roadmaps the
> change could affect.

The server resolves `id`, builds the repository relationship report
(`build_relationship_report`), and filters it for the resolved artifact —
presentation-only filtering at the consumer boundary (ADR-031); no new
relationship intelligence.

Response:

```json
{
  "schema_version": "1",
  "id": "...",
  "type": "...",
  "title": "...",
  "path": "...",
  "outgoing": {"related_decisions": ["ADR-015"]},
  "incoming": [
    {"id": "...", "type": "...", "title": "...", "path": "...", "section": "related_requirements"}
  ]
}
```

- `outgoing` is the artifact's own relationship sections, keyed by
  snake_case section name in spec order, references exactly as stored (the
  stored reference is the source of truth).
- `incoming` lists artifacts whose declared references resolve to this
  artifact under resolver semantics, ordered by path then section.

### get_summary

Signature:

```text
get_summary()
```

Description (verbatim):

> Get an overview of this repository's recorded product knowledge: artifact
> counts by type, validation state, relationship health, and items needing
> attention. Call this once at the start of a session, before exploring or
> changing the repository, to learn what recorded knowledge exists and
> where it needs care.

Response is `PortfolioSummary.to_dict()` unchanged — the same contract
`rac portfolio --json` emits:

```json
{
  "schema_version": "1",
  "directory": "...",
  "recursive": true,
  "artifacts": {"total": 0, "by_type": {}, "unknown_paths": []},
  "validation": {"valid": 0, "invalid": 0},
  "completeness": {"recommended_slots": 0, "filled": 0, "ratio": 0.0},
  "relationships": {"total": 0, "valid": 0, "broken": 0, "orphaned": 0, "coverage": 0.0},
  "attention": []
}
```

### Errors

Failed lookups are structured results, not protocol errors — agents recover
from data, not exceptions. The shapes are the resolver's own (ADR-007):

```json
{"schema_version": "1", "error": "not-found", "id": "REQ-999"}
```

```json
{"schema_version": "1", "error": "duplicate", "id": "REQ-004", "paths": ["a.md", "b.md"]}
```

A not-found response from `get_artifact` or `get_related` should be followed
by `search_artifacts` — the descriptions and the error message text may say
so.

### Truncation

Every response is subject to the per-response character budget (default
10,000; ADR-033). Oversized responses are truncated at whole-item
boundaries — whole matches, whole incoming entries, whole content tail —
never mid-element. A truncated response carries:

```json
{
  "truncated": true,
  "omitted": 12,
  "hint": "Narrow the query or request a specific artifact ID."
}
```

`truncated` is absent (not false) on complete responses. Marker field names
and placement are part of the pinned contract.

## Constraints

- Exactly these four tools; adding, removing, or renaming is a decision-level
  change (ADR-030).
- All repository semantics come from Core services; the server layer may
  filter and shape, never compute (ADR-031).
- Output is deterministic and byte-stable per repository state (ADR-032),
  within the character budget (ADR-033).
- Tools accept and return the same identifiers the resolver owns, including
  aliases (ADR-026); the server never invents identifier forms.
- Response shapes reuse `to_dict()` contracts where they exist; new fields
  follow the additive rules of ADR-007.

## Rationale

Four tools, not three: `get_summary` gives the agent a session-start
orientation call — without it, the first tool use happens only after the
agent already knows an ID or keyword, which is too late for a repository it
has never seen.

Four tools, not more: every additional description dilutes the agent's
tool-selection attention, and no fifth capability serves the provable wedge
(ADR-030).

`get_summary` takes no arguments so there is no wrong way to call it — the
orientation call must be unmissable.

Descriptions name the trigger moment ("before designing or implementing…",
"whenever an artifact ID is mentioned…") because agents decide from
descriptions alone; naming the moment is what raises call rates at the
moments that matter.

## Alternatives

- A single `query(text)` mega-tool: one description cannot name four
  different trigger moments; routing becomes server-side inference.
- Per-type tools (`get_decision`, `get_requirement`, …): multiplies
  descriptions without adding capability; the type is already in the
  response.
- Raw-file tools (`read_file(path)`): bypasses resolution and invites the
  agent back into grepping — the behaviour Guide replaces.

## Accessibility

Consumers are programs, but the content is read by people in agent
transcripts: responses are plain JSON with no formatting, colour, or layout
semantics, and error and hint text is complete prose that stands alone
without the request context.

## Style Guidance

Description text is written for the deciding agent:

- second person, imperative, present tense
- the trigger moment stated explicitly ("Call this when/before…")
- the payoff stated ("so recorded decisions are respected…")
- under 75 words per description; every word competes for selection
  attention
- vocabulary matches the artifact types users see (`decision (ADR)`,
  `requirement`), never internal module names

## Open Questions

- Whether `search_artifacts` should also match body text in a later version;
  v1 deliberately pins metadata-field matching (id, title, path) as
  `find_artifacts` does today.
- Whether `get_artifact` content should offer a metadata-only mode once
  budgets meet very large artifacts.
- Whether error text should embed the follow-up suggestion or leave it to
  the description; to be settled by demo runs in v0.10.2.

## Related Requirements

- rac-agent-context-guide

## Related Decisions

- ADR-030
- ADR-031
- ADR-032
- ADR-033
- ADR-007
- ADR-026

## Related Roadmaps

- v0.10.0-guide-foundation
