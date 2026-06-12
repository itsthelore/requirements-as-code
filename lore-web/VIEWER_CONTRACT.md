# Lore export viewer — input contract

Status: **PROPOSAL**. This document defines the JSON payload the static
export viewer (`lore export --html`) consumes, as implemented in
`src/viewer/`. It is a proposal for the maintainer to reconcile with
Lore Core's actual export format — it is **not** an instruction to
modify Core. Where Core's real export differs, either Core's `--html`
path maps its data into this shape, or this contract and the viewer are
amended to match Core. Field-name casing (snake_case below) is the most
likely point of reconciliation.

## 1. Payload: `lore-export.json`

A single JSON document.

```json
{
  "schema_version": 1,
  "corpus": {
    "name": "ledgerline",
    "generated_at": "2026-06-12T00:00:00Z",
    "lore_version": "0.10.3",
    "sample": false
  },
  "artifacts": [
    {
      "id": "ADR-021",
      "type": "adr",
      "status": "accepted",
      "title": "Replace Celery with Dramatiq",
      "body_html": "<p>This supersedes ADR-005. …</p>"
    }
  ],
  "relationships": [
    { "from": "ADR-021", "to": "ADR-005", "type": "supersedes" }
  ]
}
```

### `schema_version`

Integer, currently `1`. The viewer renders any payload it can parse and
does not hard-fail on a different version, but a bump signals a breaking
shape change.

### `corpus` — minimal metadata

| field          | type    | meaning                                            |
| -------------- | ------- | -------------------------------------------------- |
| `name`         | string  | Human-readable corpus name, e.g. the repo name.    |
| `generated_at` | string  | ISO 8601 timestamp of export generation.           |
| `lore_version` | string  | Version of the Lore CLI that produced the export.  |
| `sample`       | boolean | Optional, default false. True marks demonstration data; the viewer then shows SAMPLE DATA labels in the header and footer. |

### `artifacts[]`

| field       | type   | meaning                                                  |
| ----------- | ------ | -------------------------------------------------------- |
| `id`        | string | Stable artifact ID, unique within the corpus (`ADR-021`). The viewer links occurrences of known IDs found in body text. |
| `type`      | string | Artifact family (`adr`, `standard`, …). Open set; the viewer derives its type filter from the values present. |
| `status`    | string | Lifecycle status (`accepted`, `proposed`, `superseded`, `deprecated`, `rejected`, …). Open set; the filter is derived from values present. Known statuses get semantic colour (accepted = green, rejected = error, superseded/deprecated = muted); unknown statuses render plain. |
| `title`     | string | Plain text.                                              |
| `body_html` | string | The artifact body **rendered to HTML at export time** (see trust model). |

### `relationships[]` — typed edges

Each edge is `{ "from": ID, "to": ID, "type": string }` and reads
"`from` `type` `to`" (e.g. `ADR-021 supersedes ADR-005`). Known types
and their inverse labels in the viewer:

| type         | outbound label | inbound label    |
| ------------ | -------------- | ---------------- |
| `supersedes` | supersedes →   | ← superseded by  |
| `refines`    | refines →      | ← refined by     |
| `implements` | implements →   | ← implemented by |
| `relates-to` | relates to →   | ← related to     |

The set is open: unknown edge types render grouped under their literal
type name in both directions. Edges pointing at IDs not present in the
corpus render as "(not in corpus)" rather than being dropped.

## 2. Data injection — how the JSON reaches the viewer

The built artifact must open from `file://` with **zero network
requests**. `fetch()` of a sibling JSON file fails from `file://`, as do
external module scripts, so injection works as follows:

1. **Built single-file artifact** (`dist/viewer/lore-viewer.html`): the
   corpus is embedded in the HTML as

   ```html
   <script type="application/json" id="lore-export">{…}</script>
   ```

   placed before the (inlined) application script. On boot the app reads
   `document.getElementById('lore-export')` and parses its text content.
   All JS and CSS are inlined into the same file; there are no other
   references. When Core emits `lore export --html`, it produces exactly
   this: the viewer shell with its corpus JSON substituted into that
   element (escaping `</` as `<\/` and `<!--` as `<\u0021--`,
   both valid JSON escapes, so the payload is `<script>`-safe and
   parses unchanged).

2. **Dev server / hosted multi-page build**: no inline element exists,
   so the app falls back to fetching the committed sample corpus
   (`src/viewer/sample/lore-export.sample.json`) as a normal asset.

The feature detection is exactly "inline element with non-empty text
content present → use it, else fetch".

### Build pipeline (this repo)

`npm run build:viewer` =

1. `tsc -b` — type-check;
2. `vite build --config vite.config.viewer.ts` — a dedicated
   single-entry build (one JS chunk, one CSS file, `modulePreload`
   disabled, dynamic imports inlined) into `dist/.viewer-build/`;
3. `node scripts/build-viewer-artifact.mjs` — inlines the JS and CSS
   into the HTML, strips file-referencing `@font-face` rules (below),
   injects the corpus, verifies the result has no external `src=`,
   `href=` (other than `#` anchors) or non-`data:` `url()` references,
   and writes `dist/viewer/lore-viewer.html`.

`scripts/build-viewer-artifact.mjs --corpus <path> --out <path>` builds
the artifact around any conforming export — this is the seam Core's
`--html` exporter can reuse or replicate.

### Fonts in the single-file artifact

The design system self-hosts JetBrains Mono (~190 KB of woff2). The
single-file artifact deliberately does **not** inline the fonts: the
build strips the file-referencing `@font-face` rules and the artifact
renders in the metric-compatible local mono fallback stack already
defined by the design tokens (`JetBrains Mono Fallback` /
`ui-monospace` / `Courier New`). This keeps the artifact small and
reference-free. The hosted viewer build keeps the real fonts.

## 3. Body-HTML trust model

`body_html` is rendered by the viewer **as-is** (assigned to
`innerHTML`, then known artifact IDs in text nodes are linkified). The
viewer performs **no sanitisation**. The contract is therefore:

- **Sanitisation happens at export time.** Lore Core renders trusted,
  repo-resident Markdown to HTML and is expected to emit a safe subset
  (no script elements, no event-handler attributes, no external
  resource loads). The corpus is the user's own repository content,
  viewed by the person who exported it — the same trust boundary as the
  repo itself.
- A hostile `body_html` could execute script in the viewer page. Do not
  build artifacts from untrusted exports. If exports ever cross a trust
  boundary (e.g. hosted multi-tenant viewing), sanitisation must be
  added at that boundary; the viewer itself stays a dumb renderer.
- Bodies that load external resources (`<img src="http…">`) would break
  the zero-network-request property; the export side must not emit
  them.

## 4. Viewer behaviour summary (for reconciliation)

- Read-only; no router dependency — state is hash-based
  (`#/` list, `#/artifact/<id>` detail) so deep links work from
  `file://`.
- List view: every artifact as a row; filter toggles for type and
  status derived from the corpus; debounced substring search over
  id + title + body text; result count announced via `aria-live`.
- Detail view: title, id, type/status chips, rendered body with
  cited-ID cross-links, and a related-artifacts panel grouped by edge
  type in both directions. List form only — a graph visualisation is an
  explicitly deferred decision.
- Keyboard: `/` focuses search, `Tab` walks rows, `Esc` returns from
  detail to list.
- ID linkification matches tokens of the shape
  `[A-Z][A-Z0-9]{1,11}-[0-9]{1,6}` and links only tokens that exist as
  artifact IDs in the corpus.

## 5. Sample data

`scripts/make-corpus.mjs` (run via `npm run corpus`) generates:

- `src/viewer/sample/lore-export.sample.json` — committed; a
  hand-authored 30-artifact corpus for "ledgerline", a fictional
  mid-size Python billing service. Its `corpus.name` contains
  "SAMPLE DATA" and `sample: true` is set, so every surface that shows
  corpus identity is labelled.
- `/tmp/lore-export-500.json` — a deterministic 500-artifact synthetic
  corpus for performance testing. Not committed.
