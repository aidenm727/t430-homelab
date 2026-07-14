# AI Operating Model Architecture

## Purpose

The AI Operating Model defines how the Aiden Platform selects and uses artificial intelligence for a specific task or recurring workflow.

Its purpose is to translate durable Artificial Intelligence Architecture into practical, provider-independent, evidence-backed operating decisions.

The model governs:

- Task definition.
- Model and provider selection.
- Hosted, local, and hybrid assignment.
- Data-sensitivity constraints.
- Context and tool requirements.
- Evaluation evidence.
- Failure and fallback behavior.
- Human approval boundaries.

It does not rank products permanently or authorize automatic routing.

---

## Core Principle

Select the simplest approved AI arrangement that can perform the defined task responsibly.

Selection should begin with the task, required capability, data sensitivity, and authority boundary.

It should not begin with a favored provider, model release, benchmark, or product ranking.

---

## Architectural Ownership

`docs/architecture/ai.md` owns durable Artificial Intelligence and Personal AI architecture.

This document owns recurring operational decisions about:

- Which AI capability a task requires.
- Which provider or model is currently suitable.
- Whether processing may be hosted, local, or hybrid.
- What evidence supports the choice.
- What constraints and fallbacks govern use.

`docs/architecture/knowledge-authority.md` owns knowledge classes, authority, provenance, and promotion.

Platform Direction and Governance owns human authority and adoption criteria.

Security, Privacy, and Resilience owns security-sensitive constraints.

---

## Decision Unit

The operating model evaluates a defined task or recurring workflow.

A task profile should identify:

- Goal.
- Human outcome or platform responsibility.
- Primary capability.
- Consequence if the result is wrong.
- Required result quality.
- Data-sensitivity class.
- Required context.
- Required tools or integrations.
- Whether external action is permitted.
- Latency tolerance.
- Cost tolerance.
- Portability requirements.
- Validation method.
- Human approval points.
- Fallback behavior.

A vague request should be clarified or bounded before provider selection.

---

## Selection Criteria

A model, provider, or tool should be evaluated against the task using the following criteria.

### Capability Fit

- Reasoning quality.
- Domain competence.
- Coding or tool-use ability where needed.
- Multimodal capability where needed.
- Context-window and retrieval fit.
- Structured-output reliability.

### Result Quality

- Correctness.
- Completeness.
- Usefulness.
- Source quality.
- Uncertainty handling.
- Reproducibility where practical.

### Behavioral Reliability

- Scope preservation.
- Instruction following.
- Tool-use reliability.
- Repair behavior.
- Frequency of human correction.
- Stability across repeated uses.

### Data and Provider Fit

- Data-sensitivity compatibility.
- Privacy and retention terms.
- Provider access and account controls.
- Data minimization.
- Local-control requirements.
- Policy constraints when relevant.

### Operating Fit

- Cost.
- Latency.
- Availability.
- Rate limits.
- Integration burden.
- Maintenance burden.
- Energy and hardware burden.
- Failure recovery.
- Provider portability.

### Agency Fit

- Does the arrangement improve understanding or action?
- Does it preserve human judgment?
- Does it avoid unnecessary dependence?
- Does it make future improvements easier?
- Is an existing capability already sufficient?

No one criterion is always dominant.

Security, privacy, authority, and consequence may disqualify an otherwise capable option.

---

## Selection Workflow

A normal selection should follow:

```text
Define Task
  -> Classify Data and Consequence
  -> Define Authority Boundary
  -> Identify Acceptable Deployment Environments
  -> Compare Available Evidence
  -> Select the Simplest Adequate Arrangement
  -> Execute Within Scope
  -> Validate the Result
  -> Record Useful Evidence
  -> Reassess When Evidence Changes
```

Selection is contextual.

The same model may be appropriate for one task and inappropriate for another.

---

## Deployment Assignment

### Hosted AI

Hosted AI is appropriate when:

- The task benefits materially from frontier capability or hosted tools.
- The data class permits the provider.
- Retention and privacy terms are acceptable.
- External dependency is an acceptable tradeoff.
- Local capability would be meaningfully worse or more burdensome.

Public data may generally use approved hosted AI.

Ordinary Personal data may use approved hosted AI when use is purposeful, minimized, provider-aware, and proportionate.

Sensitive data requires deliberate review before hosted use.

Highly Restricted data must not be sent to general hosted AI services.

### Local AI

Local AI is appropriate when:

- Privacy or control provides meaningful value.
- Offline operation matters.
- Low-latency local integration matters.
- Repeated volume justifies operating cost.
- The local model is capable enough for the task.
- The maintenance burden is proportionate to value.

Local processing does not remove the need for access control, data minimization, validation, updates, backups, and operational security.

Local AI should not be adopted merely to satisfy an ideology of self-hosting.

### Hybrid AI

Hybrid AI is appropriate when a workflow benefits from deliberate separation.

Examples include:

- Local preparation or redaction followed by hosted reasoning.
- Hosted research followed by local sensitive synthesis.
- Hosted generation followed by deterministic local validation.
- Local retrieval with a separately approved hosted model.

Hybrid assignment should initially be explicit and human-reviewed.

The architecture does not currently authorize automatic model routing.

---

## Data-Sensitivity Operating Rules

### Public

May generally be processed by approved hosted, local, or hybrid systems.

Normal source, copyright, reliability, and cost constraints still apply.

### Ordinary Personal

Use should be purposeful and minimized.

Approved hosted processing may be acceptable when provider terms and task value justify it.

Avoid sending unrelated personal history merely because context is available.

### Sensitive

Use requires an explicit reason, minimized context, provider and retention review, and a clear validation or human-review boundary.

Local processing is preferred when it is sufficiently capable and meaningfully reduces exposure.

Sensitive data should not be included in reusable context by default.

### Highly Restricted

Must not be sent to general hosted AI systems.

Passwords, API keys, private keys, tokens, recovery codes, and similarly compromising information should be handled through deterministic secret-management workflows rather than model context.

Highly Restricted data must not be committed to the repository.

---

## Context Rules

The selected AI arrangement should receive only the context needed for the task.

Context should identify:

- Authority class.
- Source.
- Freshness.
- Relevance.
- Conflicts.
- Unknowns.
- Omitted information when omission matters.

Canonical knowledge should be preferred over conversational recollection.

Generated context may summarize canonical sources but remains derived.

Candidate findings must remain visibly non-canonical.

Task-scoped context compilation remains a future capability represented by EO-2026-013.

---

## Action and Approval Rules

AI use should preserve the action boundary defined in `docs/architecture/ai.md`.

An operating decision should identify whether the system may:

1. Explain.
2. Recommend.
3. Prepare a reviewable artifact.
4. Execute bounded reversible work.
5. Request approval.
6. Perform a separately authorized high-impact action.

General task approval does not silently authorize:

- Architecture changes.
- Mission changes.
- Production changes.
- Destructive operations.
- Credential access.
- External communication.
- Publishing.
- Financial commitments.
- Repository pushes.
- Writable-scope expansion.

---

## Evidence and Evaluation

Provider and model choices should be supported by task-relevant evidence.

Useful evidence may include:

- Verified task outcomes.
- Repeat-use consistency.
- Validation results.
- Human corrections.
- Failure patterns.
- Tool-use success.
- Scope violations.
- Latency and cost observations.
- Privacy and retention terms.
- Portability and integration experience.

External benchmarks, rankings, release notes, and commentary may inform evaluation.

They do not become architecture or permanent selection decisions.

Evidence should be refreshed when:

- The task changes.
- The provider changes materially.
- A model is replaced.
- Privacy or retention terms change.
- Reliability degrades.
- Cost or operational burden changes.
- A better existing capability becomes available.

The platform does not require one universal AI score.

---

## Failure and Fallback

An AI arrangement should define a fallback when practical.

Possible fallbacks include:

- Retry with reduced scope.
- Request missing context.
- Switch to a previously validated provider.
- Use deterministic tooling.
- Require human completion.
- Stop when sensitivity or authority is unclear.
- Preserve a candidate finding for later review.

A model should not expand scope or authority to repair its own failure.

Repeated failures should become evaluation evidence or an Engineering Opportunity when they reveal a durable platform gap.

---

## Personal AI Boundary

Personal AI may consume this operating model when selecting or recommending an AI arrangement.

Personal AI must not:

- Rewrite the operating model conversationally.
- Treat provider preference as permanent architecture.
- Send data to an environment that violates sensitivity rules.
- Promote findings into canonical knowledge automatically.
- Expand action authority silently.
- Depend on automatic routing before that capability is designed and approved.

Personal AI implementation remains deferred.

---

## Initial Operating Boundary

The initial operating model is documentation-first and human-applied.

It does not require:

- Automatic routing.
- A model registry service.
- A permanent leaderboard.
- Local-model infrastructure.
- Embeddings or vector databases.
- Autonomous agents.
- Whole-life data ingestion.
- A new Repository Object type.

Manual use should establish evidence before automation is considered.

---

## Verification Questions

Before adopting an AI arrangement, answer:

1. What defined task is being performed?
2. Which durable capability improves?
3. What data and context are required?
4. What is the sensitivity class?
5. What consequence follows from an incorrect result?
6. What action authority is granted?
7. Why is this provider, model, or deployment appropriate?
8. What evidence supports that choice?
9. How will the result be validated?
10. What fallback exists?
11. Can the workflow move to another provider?
12. Is the operating burden justified?

---

## Canonical Relationships

- `docs/architecture/ai.md` owns durable AI and Personal AI architecture.
- `docs/architecture/knowledge-authority.md` owns knowledge authority and promotion.
- `docs/vision.md` owns human authority and durable platform principles.
- `docs/architecture/capabilities.md` owns capability identity.
- `docs/roadmaps/platform-strategy.md` owns strategic sequencing.
- `docs/current-mission.md` owns active work.
- EO-2026-008 preserves the strategic AI Engineering Excellence direction.
- EO-2026-009 preserves the Personal AI Platform direction.
