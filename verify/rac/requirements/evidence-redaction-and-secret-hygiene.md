---
schema_version: 1
id: LV-KVW5PYZ925KG
type: requirement
tags: [user-facing, security, secrets, privacy, redaction]
---
# Requirement: Evidence Redaction and Secret Hygiene

## Status

Proposed

Classification: `[user-facing]` — by design the trace is the durable, committed,
PR-attached review surface, and the agent logs into live targets. Without
redaction the product's happy path leaks authenticated-session secrets and PII
into git history and public PRs. Derives from the threat model in LV-ADR-003.

## Problem

`lore-verify` drives live targets with real credentials and makes the resulting
trace/video the review artifact a reviewer reads in the PR
(`faithful-session-to-test` REQ-004, v0.2.0-breadth Initiative 5). Playwright
traces capture network headers, request/response bodies, and DOM by default —
i.e. bearer tokens, session cookies, `Authorization` headers, `.env` values, and
production PII. Committing or attaching that trace, or hardcoding a captured token
into the emitted test, leaks live secrets into git history and public review
surfaces. Nothing currently records that evidence must be safe to share before it
is persisted, and the corpus elsewhere conflates *target* credentials with the
*AI-provider* credentials of RAC ADR-035.

## Requirements

- [REQ-001] Before any trace, video, screenshot, or log is written to disk, committed, or attached to a PR, `lore-verify` MUST redact secrets from it — auth tokens, session cookies, `Authorization` and other credential headers, and known `.env`/secret-store values.
- [REQ-002] `lore-verify` MUST redact known production PII from persisted evidence, or capture against non-PII / synthetic data, so a committed artifact is safe to share.
- [REQ-003] A compiled test MUST NOT contain a hardcoded secret; credentials MUST be referenced indirectly and injected at run time (LV-ADR-002), never embedded as a literal in the artifact.
- [REQ-004] Target credentials MUST be treated as distinct from AI-provider credentials (RAC ADR-035), MUST be least-privilege and non-admin where the target allows, and MUST never be written to a trace, test, log, or any committed artifact.
- [REQ-005] Redaction MUST be fail-closed: if `lore-verify` cannot confirm an evidence artifact has been redacted, it MUST refuse to persist or attach it rather than emit it unredacted.
- [REQ-006] The redaction step MUST be auditable: `lore-verify` MUST record that redaction ran for each persisted artifact, so a reviewer can trust the committed evidence was scrubbed.

## Acceptance Criteria

- A run that authenticates against a target produces a committed trace containing
  no bearer token, session cookie, or `Authorization` header value.
- A compiled test emitted from an authenticated session contains no literal
  credential; the credential is referenced and injected at run time.
- When redaction cannot be confirmed, the run fails closed and persists nothing.

## Success Metrics

- Zero secrets or production PII are detectable in any committed test, trace, or
  PR-attached artifact across the test corpus, verified by a scanning check.

## Risks

- Redaction misses a non-standard secret format and leaks it. Mitigation: a
  conservative default denylist plus fail-closed behaviour (REQ-005), and a scan
  in the run summary; broaden patterns as targets reveal new formats.
- Over-redaction destroys the evidence's review value. Mitigation: redact values,
  not structure — keep the request/flow visible while masking secret values.

## Assumptions

- Playwright (or the chosen driver) exposes hooks to scrub network/DOM capture
  before the trace is finalised.
- Targets can be exercised against synthetic or non-PII data for the cases where
  redaction of real PII is impractical.

## Related Decisions

- lv-adr-003-runtime-threat-model
- lv-adr-001-product-identity

## Related Requirements

- faithful-session-to-test
- production-target-safety

## Related Designs

- runner-interface-and-target-config
- verified-by-write-back
