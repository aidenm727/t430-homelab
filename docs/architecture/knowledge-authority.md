# Knowledge Authority Architecture

## Purpose

Knowledge Authority defines how the Aiden Platform distinguishes information classes, identifies canonical ownership, preserves provenance, resolves conflict, and deliberately promotes useful findings into authoritative knowledge.

Its purpose is to prevent temporary conversation, generated context, AI output, execution evidence, and candidate findings from silently acquiring authority.

This architecture generalizes the Canonical Knowledge Promotion Workflow represented by EO-2026-020 beyond engineering-only use.

---

## Core Principle

Information becomes canonical through deliberate ownership and review.

It does not become canonical because it was generated confidently, stored in the repository, repeated frequently, remembered by an assistant, or produced by a successful execution.

Promotion changes authority.

Copying changes location.

The two are not equivalent.

---

## Architectural Ownership

`docs/architecture/repository.md` owns the repository source-of-truth hierarchy and placement rules for engineering knowledge.

This document owns:

- Knowledge authority classes.
- Promotion requirements.
- Provenance.
- Canonical-owner selection.
- Acceptance, rejection, and deferral.
- Conflict handling.
- Historical traceability.
- Personal AI consumption boundaries.

`docs/architecture/ai-operating-model.md` owns AI selection and operating decisions.

Canonical domain documents own the knowledge deliberately promoted into them.

---

## Authority Is Independent of Format

Authority is not determined by file format, storage location, or interface.

Examples:

- A generated Markdown file in Git may remain non-canonical.
- A YAML Repository Object may be canonical for its object state.
- A terminal transcript may be evidence without being architecture.
- A conversation may reveal a useful finding without owning it.
- A live verification result may override an outdated infrastructure record while creating an obligation to update the record.
- An external source may be authoritative for an external fact without becoming repository-owned platform knowledge.

Every important item should be understood by authority class and owner.

---

## Knowledge and Evidence Classes

### Canonical Knowledge

Reviewed knowledge owned by a designated source.

Examples include:

- Vision.
- Architecture.
- Standards.
- Current Mission.
- Infrastructure records.
- Operations records.
- Roadmaps.
- Registered Repository Objects.
- Human decisions recorded in their canonical owner.

Canonical knowledge may still become outdated or wrong.

Authority means it is the current owned record, not that it is infallible.

### Source Records and Evidence

Information used to support a conclusion.

Examples include:

- Primary documents.
- Research papers.
- Provider documentation.
- Terminal output.
- Test results.
- Measurements.
- Logs.
- Emails.
- Live system inspection.
- External records.

Evidence should retain source, date, and relevant context.

Evidence does not automatically own the conclusion drawn from it.

### Generated Context

Rebuildable material derived from canonical or source records.

Examples include:

- `docs/aiden-context.md`.
- `docs/infrastructure-snapshot.md`.
- Future task context packages.
- Generated summaries.

Generated context should identify its sources and managing process.

It may be useful and accurate while remaining non-canonical.

### Personal Context

Purposeful information about the owner used to improve assistance or workflows.

Personal context may be temporary, source-backed, inferred, or canonically recorded.

Its authority and sensitivity must be explicit.

Personal context should not be treated as permanent truth merely because an AI system remembers it.

### Temporary Conversation

Short-lived interactive context used to understand the current exchange.

Conversation may explain intent, reveal evidence, produce candidate findings, or authorize a bounded action.

Conversation does not replace canonical repository knowledge.

Important durable conclusions should be promoted to an appropriate owner.

### Execution Records

Evidence of what a human, tool, automation, or agent attempted and observed.

Execution records may include:

- Task identity.
- Inputs.
- Commands.
- Changes.
- Validation.
- Failures.
- Repair attempts.
- Approvals.
- Final disposition.

Execution records do not automatically become architecture, mission state, or completed-action truth.

### Candidate Findings

Potentially useful conclusions that have not been accepted by a canonical owner.

A candidate finding should expose:

- Statement.
- Source.
- Evidence.
- Author or producing system.
- Date or freshness.
- Confidence or uncertainty.
- Relevant sensitivity.
- Proposed owner when known.
- Conflicts or unresolved questions.

Candidate findings remain non-canonical until reviewed.

### Decisions

Human-authorized choices recorded by the responsible owner.

A decision should identify:

- What was decided.
- Why.
- Evidence considered.
- Authority.
- Date.
- Consequences.
- Revisit conditions when useful.

A recommendation is not a decision.

### Completed Actions

Verified changes or events that actually occurred.

A plan, command, generated artifact, or agent claim is not a completed action.

Completion should be supported by appropriate evidence such as repository state, live verification, external confirmation, or an operational record.

### Unknown or Conflicting Information

Information whose authority, correctness, freshness, or interpretation is unresolved.

Unknown and conflicting states should remain visible.

They should not be normalized into false certainty.

---

## Canonical Ownership Selection

A promotion proposal should identify the one canonical owner responsible for the durable knowledge.

Examples:

- Purpose and direction -> `docs/vision.md`.
- Platform structure -> `docs/architecture/platform.md`.
- Capability identity -> `docs/architecture/capabilities.md`.
- AI architecture -> `docs/architecture/ai.md`.
- AI operating rules -> `docs/architecture/ai-operating-model.md`.
- Knowledge authority -> this document.
- Active work -> `docs/current-mission.md`.
- Deployed state -> infrastructure records.
- Repeatable expectations -> standards.
- Change evidence -> operations.
- Future sequencing -> roadmaps.
- Structured entity state -> the registered Repository Object.

A proposal without a responsible owner should remain a candidate or motivate an architecture decision.

Do not create a new owner merely to avoid integrating an existing one.

---

## Canonical Knowledge Promotion Workflow

A normal promotion should follow:

```text
Capture Candidate
  -> Preserve Provenance
  -> Classify Sensitivity
  -> Identify Canonical Owner
  -> Check Freshness and Conflict
  -> Prepare Proposed Change
  -> Human Review
  -> Accept, Reject, or Defer
  -> Apply to Canonical Owner
  -> Validate and Synchronize
  -> Preserve Decision Traceability
```

### Capture Candidate

Preserve the useful finding without presenting it as canonical.

Capture may occur in temporary notes, a review artifact, an execution record, a proposed patch, or a future registered candidate object.

### Preserve Provenance

Record enough information to understand where the finding came from.

Provenance should include:

- Source or sources.
- Date or freshness.
- Producing human, tool, workflow, or model when relevant.
- Relevant task or execution identity.
- Transformations or summarization.
- Confidence and uncertainty.
- Sensitivity constraints.

### Classify Sensitivity

Determine whether the candidate contains Public, Ordinary Personal, Sensitive, or Highly Restricted information.

Promotion must not expose data beyond its approved boundary.

Highly Restricted information should not be placed into ordinary canonical documents.

### Identify Canonical Owner

Select the existing source responsible for the durable fact or decision.

If ownership is ambiguous, resolve architecture before promotion.

### Check Freshness and Conflict

Compare the candidate with:

- Existing canonical knowledge.
- Newer evidence.
- Conflicting sources.
- Live verification where relevant.
- Current mission and architecture.

Conflict should be exposed rather than overwritten silently.

### Prepare Proposed Change

Translate the candidate into a reviewable change to the canonical owner.

The proposal should preserve the distinction between:

- Existing text.
- New evidence.
- Interpretation.
- Decision.
- Generated wording.

### Human Review

A human with the relevant authority reviews:

- Usefulness.
- Evidence.
- Ownership.
- Sensitivity.
- Conflict.
- Scope.
- Consequence.
- Maintenance burden.

AI may explain, critique, and prepare.

AI does not approve promotion by itself.

### Decide

The candidate may be:

- Accepted.
- Rejected.
- Deferred.
- Superseded.
- Returned for more evidence.
- Redirected to another owner.

The decision should be explicit when the candidate is important or likely to recur.

### Apply to Canonical Owner

Accepted knowledge is written to the designated owner.

Promotion should not duplicate the full fact across several canonical documents.

Other documents should reference the owner.

### Validate and Synchronize

Run the verification appropriate to the owner.

For repository engineering knowledge, this normally includes:

- Document registration when needed.
- Generated-context regeneration.
- Repository validation.
- Repository synchronization.
- Engineering Review.
- Commit and push.

### Preserve Traceability

Retain enough history to understand:

- Which candidate was considered.
- Which evidence supported it.
- What decision was made.
- Where accepted knowledge now lives.
- Why a candidate was rejected or deferred when that matters.

Git history may provide part of the trace.

A future decision or promotion record may provide more when repeated use proves the need.

---

## Acceptance Criteria

A candidate is ready for promotion when:

- The knowledge is durable enough to preserve.
- The evidence is sufficient for the consequence.
- A canonical owner exists.
- The proposal does not create unnecessary duplication.
- Sensitivity handling is appropriate.
- Conflicts are resolved or explicitly represented.
- Human review has occurred.
- The resulting change remains understandable and maintainable.

Not every useful observation should become canonical.

---

## Rejection and Deferral

Rejecting or deferring a candidate does not imply that the source was worthless.

A candidate may be rejected because it is:

- Incorrect.
- Unsupported.
- Duplicative.
- Too temporary.
- Owned elsewhere.
- Too sensitive for the proposed destination.
- Too costly to maintain.
- Premature.
- Outside current platform scope.

Deferred candidates should preserve their unresolved condition when future value is plausible.

Repeated rejected or deferred candidates may reveal a missing capability or poor intake process.

---

## Conflict Handling

When sources disagree:

1. Preserve the disagreement.
2. Identify source authority and freshness.
3. Prefer live verification for current operational reality.
4. Prefer canonical architecture for intended design.
5. Avoid overwriting history to create false consistency.
6. Record the human decision when the conflict is consequential.
7. Update stale canonical owners after verification.

An AI system should not choose silently between conflicting sources.

---

## Personal AI Consumption Rules

Personal AI may consume canonical knowledge, generated context, personal context, source records, execution records, and candidate findings.

It must:

- Preserve authority labels.
- Expose important provenance.
- Distinguish retrieval from inference.
- Distinguish recommendation from decision.
- Identify uncertainty and conflict.
- Respect sensitivity boundaries.
- Prefer canonical owners for durable platform facts.
- Request review before promotion.

Personal AI must not:

- Treat memory as canonical automatically.
- Present generated context as the source of truth.
- Convert repeated conversation into authority.
- Promote its own findings automatically.
- Rewrite canonical ownership conversationally.
- Hide conflicting evidence.
- Claim an action completed without verification.

---

## Relationship to Repository Objects

Repository Objects may preserve canonical structured entity state.

A future candidate, decision, or promotion object may become useful.

This architecture does not create a new Repository Object type yet.

A new object type should be introduced only after repeated promotion workflows reveal stable shared requirements.

Until then, reviewed documents, proposed changes, operational evidence, and Git history are sufficient.

---

## Relationship to EO-2026-020

EO-2026-020 identified the need for a controlled Canonical Knowledge Promotion Workflow.

This architecture establishes that workflow as a platform-wide Knowledge and Context responsibility.

The opportunity remains in `reviewed` lifecycle state until a separate human-authorized lifecycle decision records whether the architecture satisfies enough of its intent to progress.

No lifecycle mutation occurs through this document.

---

## Initial Operating Boundary

The initial Knowledge Authority foundation is documentation-first and human-applied.

It does not require:

- Automatic knowledge promotion.
- Whole-life ingestion.
- A universal personal database.
- Embeddings or a vector database.
- Autonomous conflict resolution.
- A new Repository Object type.
- Permanent storage of every conversation.
- Personal AI implementation.

Manual use should establish the correct records and boundaries before automation.

---

## Verification Questions

Before promoting knowledge, answer:

1. What is the candidate statement?
2. What authority class does it currently have?
3. Which evidence supports it?
4. How fresh is the evidence?
5. What sensitivity constraints apply?
6. Does conflicting information exist?
7. Which canonical owner is responsible?
8. What human authority is required?
9. What exact change is proposed?
10. How will the change be validated?
11. How will acceptance, rejection, or deferral remain traceable?
12. Does promotion increase agency enough to justify maintenance?

---

## Canonical Relationships

- `docs/architecture/repository.md` owns repository authority and placement.
- `docs/architecture/ai.md` owns durable AI architecture.
- `docs/architecture/ai-operating-model.md` owns AI operating decisions.
- `docs/architecture/capabilities.md` owns Knowledge and Context capability identity.
- `docs/vision.md` owns human authority and durable principles.
- `docs/standards/engineering-collaboration.md` owns repeatable engineering collaboration behavior.
- EO-2026-011 preserves the Documentation Intelligence capability opportunity.
- EO-2026-013 preserves task-scoped context compilation.
- EO-2026-020 preserves the Canonical Knowledge Promotion Workflow opportunity.
