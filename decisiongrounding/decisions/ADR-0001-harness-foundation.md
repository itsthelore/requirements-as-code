---
schema_version: 1
id: DG-ADR-0001
type: decision
tags: [harness, foundation, methodology]
---

# ADR-0001: Harness Foundation

## Status

Accepted

## Category

Architecture

## Context

`decisiongrounding` is a reproducible benchmark that asks one question:

> Does a deterministic decision-grounding layer make a coding agent adhere to
> a team's *prior decisions* better than (a) dumping all the decision docs
> into context, (b) commodity RAG over the same docs, or (c) a general-purpose
> memory layer — and at what corpus size does any difference appear?

The benchmark must stay credible to a skeptical investor or staff engineer,
*including when the result is unfavorable to the grounding layer*. That places
hard constraints on the harness: threatening baselines (`context_dump`,
`naive_rag`) are mandatory; the answering model is held constant across arms;
each arm gets one symmetric opportunity to populate the answering model's
context; scoring is deterministic and structural wherever possible; results
are pre-registered and append-only.

Before writing harness code we must decide what to build the harness *on*.
Two options were evaluated.

### Option A — Build inside Supermemory MemoryBench

Implement `decisiongrounding` as a custom benchmark plus a custom provider
inside Supermemory's MemoryBench framework
(https://supermemory.ai/docs/memorybench/overview), reusing its existing
Mem0 / Zep / Supermemory provider adapters.

#### Advantages

- The memory-provider arms (`memory_provider`) come almost for free via
  MemoryBench's existing adapters.
- Third-party framework provenance lends external credibility — results are
  not "graded on our own homework's grading software."
- Less harness plumbing to write and maintain.

#### Disadvantages

- MemoryBench's evaluation contract is **conversational QA**: ingest a
  transcript, `search` it, then have a judge grade a free-text answer. Our
  task is **plan-then-structurally-check**: the agent proposes a concrete
  change and we inspect the *structure* of that proposal (did it propose the
  prohibited migration? did it follow the superseded decision?). Bending a
  conversational-QA contract around a structural-check task invites subtle
  mismatches precisely where our headline metric lives.
- It couples our headline (deterministic decision-adherence rate) to a
  framework whose center of gravity is an LLM judge — the opposite of our
  "deterministic scoring first" constraint.
- It makes our reproducibility surface (pinned answering model, append-only
  results, seed) a function of an upstream project's release cadence.

### Option B — Standalone harness, borrowing MemoryBench's conventions

Build a small standalone harness that owns its evaluation contract, borrowing
only MemoryBench's *good conventions*: the provider-adapter pattern, pinned
model versions, and append-only run storage.

#### Advantages

- The evaluation contract fits the task exactly: a uniform `Provider` adapter
  (`prepare(corpus)` / `respond(task) -> ProposedChange`) feeds a held-constant
  answering model, and a deterministic scorer inspects the proposed change.
- Deterministic structural scoring stays the headline; the LLM judge is a
  documented, disclosed *fallback* for genuinely open-ended cases — not the
  spine.
- Full control over reproducibility: pinned model + version + temperature +
  seed, append-only `results/`, frozen `spec/`.
- The memory-provider arms are still reachable — `providers/memory_provider.py`
  is a MemoryBench-style adapter slot we fill later, so we lose none of
  Option A's reach, only its coupling.

#### Disadvantages

- We write and maintain the harness plumbing ourselves.
- Third-party credibility is earned through method transparency
  (`CONTRIBUTING.md`, pre-registration, published losing results) rather than
  inherited from a known framework.

## Decision

Adopt **Option B**: a standalone harness that borrows MemoryBench's
provider-adapter pattern, pinned-model discipline, and append-only run storage,
but owns a plan-then-structurally-check evaluation contract with deterministic
scoring as the headline.

The decisive factor is the evaluation-contract mismatch. Our credibility rests
on deterministic, structural decision-adherence scoring; MemoryBench's contract
is conversational QA graded by an LLM judge. Borrowing its conventions costs us
nothing we need, while inheriting its contract would put a semantic judge on
the critical path of our headline metric. Option A's one real advantage —
near-free memory-provider arms — is preserved under B through a MemoryBench-style
adapter slot (`providers/memory_provider.py`).

## Consequences

### Positive

- The harness contract matches the task; the headline metric stays
  deterministic.
- Reproducibility (pinned model, seed, append-only results) is fully under our
  control.
- Arms differ only in how they assemble grounding context; the answering model
  and prompt scaffold are held constant, isolating retrieval/assembly quality.

### Negative

- We own more code than Option A would require.
- Memory-provider arms require us to write the adapter rather than inherit it.

### Risks

- **Self-grading perception.** A standalone harness can be dismissed as
  "grading your own homework." Mitigation: pre-registered `spec/`, append-only
  `results/`, blind gold-labeling, and a published commitment to release losing
  results (`CONTRIBUTING.md`).
- **Scaffold-simulated results.** The offline demo answering model simulates
  the crossover by construction. Mitigation: the README and this ADR state
  plainly that stub output is a plumbing illustration, not a benchmark result;
  the headline remains an unvalidated hypothesis until the pinned Claude
  answering model runs on real/public-derived corpora.

## Alternatives Considered

See Option A and Option B above. Option A was rejected for evaluation-contract
mismatch, not for lack of merit; its memory-provider reach is retained under B.

## Related Decisions

- (none yet — this is the foundation decision)

## Success Measures

- The two threatening arms (`context_dump`, `naive_rag`) run end-to-end on a
  tiny corpus with no credentials.
- Scoring is deterministic for all five scenario types; no LLM judge is on the
  critical path of the headline metric.
- A reviewer can reproduce a run from seed + pinned model versions, and
  `results/` only ever grows.

## Review Date

Revisit if a memory-provider arm forces ingestion semantics that the
standalone contract cannot express cleanly, or if MemoryBench adds a
structural-check evaluation mode.
