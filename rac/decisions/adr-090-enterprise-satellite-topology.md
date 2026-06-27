---
schema_version: 1
id: RAC-KW47GN4SB403
type: decision
---
# ADR-090: Enterprise Satellite Topology

## Status

Proposed

## Category

Architecture

## Context

Beyond configuration, the enterprise asks are network, SDK, and write-back work:
ingest from and publish to Confluence, resolve and comment on Jira, gate CI on
Bitbucket and Jenkins, aggregate audit logs to a sink, and package the whole for
Kubernetes. ADR-064, ADR-068, and ADR-073 already establish that such work lives
in satellite repositories that depend only on the published package, CLI, and
export contracts — never engine internals. This decision names the enterprise
satellites and the boundaries they honour, so the engine-side contracts they
imply are visible in one place.

## Decision

Enterprise integrations are delivered as a small constellation of satellites, kept
deliberately few rather than one-per-integration.

- **`lore-atlassian`** — one satellite for the Atlassian suite (shared Cloud
  auth):
  - inbound Confluence ingest, feeding `rac ingest` and the existing human-review
    loop (ADR-072, ADR-006);
  - outbound Confluence publish as a managed block, reusing the `agent_rules`
    managed-block pattern;
  - Jira external-edge resolution and state checks (ADR-087);
  - gatekeeper comment-mode, posting a blocking decision to the linked Jira
    ticket and Confluence page.
- **`lore-pipelines`** — a Bitbucket Pipelines pipe and a Jenkins shared-library
  wrapper over the already-CI-neutral `rac gate` (ADR-049, ADR-054).
- **`lore-audit`** — a collector that tails the ADR-084 audit JSONL to a sink
  (Loki, S3, Elastic), shipped as a GitHub Action and a Bitbucket pipe.
- Optional Helm/ArgoCD packaging lays down `lore-watchkeeper`, `lore-audit`, and
  the Confluence sync cron as deployable applications.

Boundaries every enterprise satellite honours:

- Consumes only published contracts — the CLI, the `--documents` and `--graph`
  exports, and the audit JSONL — never engine internals (ADR-063, ADR-073).
- All write-back is propose-only through human pull-request review (ADR-065,
  ADR-077); RAC never becomes a write-through path into a document platform.
- Adds no network code to the engine; satellites own all network and SDK
  dependencies (ADR-002).

Engine-side contracts this topology implies (recorded here, each built under its
own ADR): the audit JSONL (ADR-084), the external-edge graph marker (ADR-087,
ADR-074), and a Bitbucket Code-Insights output format alongside SARIF
(an ADR-054 extension).

## Consequences

### Positive

- One place names the enterprise satellites and the rules they obey, so the
  engine stays the engine and the contracts they need are explicit.
- Consolidating Atlassian into one satellite matches the single shared auth and
  the cross-product comment-mode, avoiding two repos that share one auth layer.

### Negative

- Several satellites pinned to the export contract mean continuous
  conformance-test carry against each engine release (ADR-073); the cost is real
  and must be invested in, not assumed free.
- A cross-satellite bug has no single owning repo; coordination falls to the
  contracts and the reference configuration (ADR-091, the paved-path example).

### Risks

- An integration grows a network dependency back into the engine. Mitigation:
  the boundary rules are recorded here; the engine gains no network import
  (ADR-002).
- Write-back becomes a bypass of PR review. Mitigation: propose-only via PR is a
  named boundary (ADR-065, ADR-077).

## Alternatives Considered

### One repository per provider/integration

Separate `lore-confluence`, `lore-jira`, `lore-bitbucket`, and so on.

#### Disadvantages

- Fragments shared auth and the cross-product comment-mode; more repos to keep
  green against the contract (ADR-073). Consolidation is the cheaper carry.

### In-engine connectors

Build the network/SDK work into `rac-core`.

#### Disadvantages

- Contradicts ADR-002 and the single-fenced-ping rule; the engine stops being
  offline and deterministic. Rejected.

A small consolidated constellation of contract-consuming satellites is selected.

## Relationship to Other Decisions

- ADR-064, ADR-068, ADR-073, ADR-063: the satellite model and the
  contract-consumer boundary this decision applies.
- ADR-084: the audit JSONL the `lore-audit` collector consumes.
- ADR-087, ADR-074: the external-edge graph marker `lore-atlassian` resolves.
- ADR-049, ADR-054: the CI-neutral gate and SARIF output `lore-pipelines` wraps.
- ADR-065, ADR-077: write-back is propose-only via PR.
- ADR-072, ADR-006: inbound ingest reuses the conversion and human-review loop.
- ADR-085: the distribution half of "configuration plus distribution, not a
  mode".
