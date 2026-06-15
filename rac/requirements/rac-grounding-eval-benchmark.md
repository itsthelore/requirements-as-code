---
schema_version: 1
id: RAC-KV6KFF98VDBX
type: requirement
tags: [user-facing, eval, retrieval, benchmark, ci]
---
# Requirement: Grounding Retrieval Benchmark

## Status

Proposed

Classification: `[user-facing]` — it is the proof the tool works. Scoped to the
v0.23.0 hardening release (WS1).

## Problem

Lore's core claim is that an agent retrieves the right recorded decision at the
right moment. Today that claim rests on unit tests of individual behaviors and
on demo anecdote; nothing measures aggregate retrieval quality or guards against
silent regressions. The failure that matters most — surfacing a superseded
decision as if it were current — is exactly what Lore exists to prevent, yet
there is no gate that fails the build when it happens.

## Requirements

- [REQ-001] RAC MUST provide a `rac eval` CLI subcommand that scores the retrieval tools against a versioned fixture corpus and query set.
- [REQ-002] Eval scoring MUST be deterministic and offline: a pure function of `(corpus, query set, retrieval code)`, with no network, no API keys, no randomness, no clock in the scored path, and no embeddings or LLM judge (ADR-066).
- [REQ-003] `rac eval` MUST compute Precision@k and Recall@k at `k ∈ {1, 3, 5}` as macro-averages reported `overall`, `by_category`, and `by_tool`, and MUST count hard-negative violations (a `must_not_return` id appearing in top-k).
- [REQ-004] Ranking MUST be byte-stable: equal-scored artifacts order by ascending artifact id, layered on the existing deterministic retrieval sort.
- [REQ-005] `rac eval` MUST write a scorecard with `metrics`, `metadata`, and `per_query` objects, and MUST record a `corpus_hash` and `query_set_hash`; only `metrics` is compared by the gate.
- [REQ-006] RAC MUST provide a `rac eval --check` CI gate that FAILS on any hard-negative violation, any gated metric below an absolute floor, or any gated metric below `baseline − tolerance`, printing which rule fired with the metric, baseline, and current values.
- [REQ-007] Re-baselining MUST be human-gated via `rac eval --update-baseline`; CI MUST NOT ever update the baseline.
- [REQ-008] The fixture corpus MUST be schema-valid, pass `rac doctor`, span all five artifact types, and include a supersession chain, distractors, and an ambiguous pair.
- [REQ-009] The eval SHOULD reuse the WS8 content-hash short-circuit so re-runs skip unchanged artifacts.

## Acceptance Criteria

- `rac eval` runs offline with no network or keys; the `metrics` object is
  byte-identical across repeated runs on an unchanged corpus.
- Three regression-injection tests prove the gate is real: a clean corpus
  passes; a deterministically removed relevant artifact drops `r_at_5` and fails
  the gate; a forced `must_not_return` id in top-k fails the gate on violations.
- The human-readable summary prints overall, by-category, and by-tool tables and
  lists every violating case with its returned ids.
- The gate is wired into CI and fails the build on regression.

## Success Metrics

- The committed baseline meets the initial floors (`negative_violations == 0`,
  `overall.p_at_1 ≥ 0.90`, `overall.r_at_5 ≥ 0.95`).
- A deliberately introduced retrieval regression is caught by CI rather than by
  a human noticing later.

## Risks

- Floors mis-calibrated before the first green run. Mitigation: calibrate from
  the first run, commit the baseline, gate on `baseline − tolerance` thereafter.
- A fixture corpus that drifts from real retrieval. Mitigation: source cases
  from real or partner-representative repos and grow from design-partner usage.

## Assumptions

- The existing deterministic retrieval surfaces (`search_artifacts`,
  `get_related`) are the right thing to benchmark and guard.

## Related Decisions

- adr-066
- adr-002
- adr-037
- adr-038
- adr-007

## Related Requirements

- rac-idempotent-content-hash-processing
- rac-single-schema-agreement

## Related Roadmaps

- v0.23.0-hardening
