---
schema_version: 1
id: LV-KVW5PYK66DZB
type: decision
tags: [security, trust, threat-model, runtime]
---
# LV-ADR-003: Runtime Threat Model and Agent-Execution Trust Boundary

## Context

`lore-verify`'s Drive module gives an autonomous LLM agent **a real browser and a
real, command-executing terminal**, pointed at live targets that may include
**production**, holding **real target credentials**. This is the single most
dangerous surface the whole programme introduces, and nothing in the corpus governs
it yet.

RAC ADR-065 ("artifact content is untrusted; the trust boundary is human PR
review") was deliberately scoped to *artifact-content* trust — it "protects the
store, not the agent" — and names execution trust nowhere. The RAC engine never
executes anything (RAC ADR-017, ADR-024), so it never needed an execution threat
model. `lore-verify` does. This decision is the execution-half analogue of
ADR-065: it records the trust boundary, the threat actors, and the controls that
bound an autonomous agent with a shell and credentials, so that every downstream
control (sandboxing, credential scope, redaction, prod-safety) derives from a
recorded model rather than being improvised by the prototype.

## Decision

`lore-verify` adopts the following threat model and trust boundary. It is binding
on Drive, Run, and any future runner.

### Threat actors and attack surfaces

1. **A hostile or compromised target.** A target web page or service can attempt
   **prompt injection** — content crafted to steer the agent into running
   attacker-chosen terminal commands, exfiltrating credentials, or navigating to
   internal resources. The target is **untrusted input**, exactly as artifact
   content is untrusted in ADR-065.
2. **A buggy or mis-steered agent.** Even absent an attacker, an autonomous agent
   can issue **destructive or unintended commands** (deleting data, mutating
   production, spending money, sending email) through the terminal or the product
   UI.
3. **The LLM provider as a data sink.** Everything the agent observes — target
   DOM, network responses, terminal output — may be sent to the model provider,
   carrying **secrets and PII** off the machine (RAC ADR-035 keeps credentials
   user-managed, but does not address what transits to the provider).
4. **The developer environment as a target.** A compromised agent with terminal
   access can read the developer's filesystem, environment, SSH keys, and other
   repos — a lateral-movement / exfiltration vector.

### Trust boundary and controls

- **The target is untrusted.** The agent MUST treat all target-derived content as
  untrusted and MUST NOT let it expand the agent's own authority (no
  target-content-driven escalation of what the terminal may run). Prompt-injection
  resistance is a design obligation of Drive, not an afterthought.
- **The terminal is sandboxed and least-authority.** Drive's terminal runs in an
  isolated environment with an explicit, minimal allowed scope (working directory,
  network egress, command set). It MUST NOT have ambient access to the developer's
  home directory, credential stores, or unrelated repos. The sandbox contract is
  specified in the design `runner-interface-and-target-config` and is fail-closed:
  absent an explicit grant, an action is denied.
- **Target credentials are least-privilege and separate from AI credentials.**
  Target login credentials are a *distinct* concept from the BYO AI-provider
  credentials of RAC ADR-035 (the corpus must not conflate them). They MUST be
  scoped, non-admin, non-destructive where possible, injected at run time (never
  compiled into an artifact, LV-ADR-002), and never written to a trace, test, or
  log (enforced by the `evidence-redaction-and-secret-hygiene` requirement).
- **Production is fail-closed.** An agent MUST NOT perform mutating actions against
  a target marked non-seedable/production unless explicitly allowlisted; this is
  enforced by the `production-target-safety` requirement, not left to agent
  judgement.
- **Provider data exposure is disclosed and minimisable.** That target content
  transits to the LLM provider is a recorded property of the product; local/
  self-hosted models (RAC ADR-035) are the mitigation for sensitive targets, and
  redaction reduces what is captured and persisted.
- **The human PR review remains the final gate.** Consistent with ADR-065, nothing
  the agent produces enters a Lore corpus except as a proposed, human-reviewed PR
  (LV-ADR-001). The agent's *output* is untrusted until reviewed, just as its
  *input* (the target) is untrusted while running.

## Consequences

Every security control in the product now has a recorded parent rationale, and the
two security requirements (`evidence-redaction-and-secret-hygiene`,
`production-target-safety`) and the sandbox section of
`runner-interface-and-target-config` are derivations of this model rather than
ad-hoc rules. The cost is real engineering: a genuine sandbox, credential scoping,
and prompt-injection-resistant Drive are non-trivial and constrain how freely the
agent can act. That cost is the point — an LLM with a shell and production
credentials is not a feature to ship casually.

Trade-off: this does not make autonomous QA *safe* in the absolute, only
*bounded*. Residual risk (a novel injection bypassing the sandbox, a provider data
incident) is accepted and disclosed rather than claimed away; the mitigations lower
likelihood and blast radius, and local models plus least-privilege credentials cap
the worst case.

## Status

Accepted

## Category

Technical

## Alternatives Considered

- **Rely on ADR-065 as the trust story.** Rejected: ADR-065 governs the integrity
  of the *stored corpus* via human review; it explicitly does not cover an agent
  *executing* with credentials. Reusing it would leave the largest attack surface
  undocumented.
- **No terminal — browser only.** Rejected: Drive needs a terminal to develop and
  exercise products (it is core to the "real developer tools" thesis); the answer
  is to sandbox the terminal, not remove it.
- **Trust the agent's judgement for prod safety / destructive actions.** Rejected:
  an autonomous, exploratory agent against production is a data-loss vector;
  safety must be fail-closed and enforced by the runner, not hoped for
  (`production-target-safety`).
- **Defer the threat model until after the prototype.** Rejected: the prototype
  *is* where Drive first runs a shell with credentials; improvising the boundary
  there is how a remote-code-execution or exfiltration vector ships. The model
  precedes the code.

## Related Decisions

- lv-adr-001-product-identity
- lv-adr-002-pluggable-runner

## Related Requirements

- evidence-redaction-and-secret-hygiene
- production-target-safety

## Related Designs

- drive-compile-run-architecture
- runner-interface-and-target-config
