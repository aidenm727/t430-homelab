# Canonical Knowledge Promotion Procedure

> **Authority:** Canonical Operations procedure
>
> **Canonical:** Yes
>
> **Generated:** No

## Purpose

This document defines the reusable manual operating procedure for deliberately promoting candidate findings into canonical knowledge.

`docs/architecture/knowledge-authority.md` owns the architecture, promotion principles, and authority requirements. This procedure operationalizes that architecture and does not replace it.

---

## Operating Boundary

This procedure is documentation-first and human-applied. It provides a reviewable operating contract without requiring Atlas automation.

It permits no automatic promotion or silent acquisition of authority. It creates no new Repository Object type and does not establish a universal intake system, database, vector store, whole-life ingestion system, Personal AI implementation, or autonomous conflict-resolution mechanism.

---

## Entry Conditions

A candidate enters this procedure only when:

- It may be durable, recurring, or consequential enough to preserve.
- It remains non-canonical.
- Its source, date or freshness, evidence, confidence or uncertainty, and sensitivity can be described.
- A proposed canonical owner can be identified, or ownership ambiguity can be exposed.
- Review and continuing maintenance are justified by the candidate's likely value.

---

## Roles and Authority

### Candidate Producer

Identifies or produces the candidate and supplies the available statement, provenance, evidence, uncertainty, and sensitivity context.

### Workflow Operator / Record Custodian

Applies this procedure, preserves the candidate record, maintains its status, and prevents preparation from being presented as acceptance or application.

### Canonical Owner

Owns the destination that would become authoritative if the candidate is accepted and applied.

### Human Decision Authority

Accepts, rejects, defers, supersedes, requests more evidence for, or redirects the reviewed candidate. Tools and AI systems do not hold this authority.

### Implementer

Applies the exact accepted proposal to the canonical owner after application scope is separately authorized.

### Verifier

Confirms that the accepted proposal was applied within scope, validation succeeded, synchronization is current, and traceability is complete.

Git and Atlas are deterministic evidence providers, not approval authorities. One human may hold multiple roles, but every role and decision must remain explicit.

---

## Required Candidate Record

Every candidate record must include:

- A title or dated identifier.
- Authority class.
- Canonical and generated status.
- Workflow status.
- Candidate statement.
- Sources and provenance.
- Producing human, tool, workflow, or model when relevant.
- Dates and freshness.
- Evidence summary and limitations.
- Sensitivity, retention, and redaction boundary.
- Confidence and uncertainty.
- Proposed canonical owner and destination section.
- Existing canonical context.
- Conflict and compatibility review.
- Exact proposed change.
- Consequences and maintenance burden.
- Validation plan.
- Required human authority.
- Decision record.
- Application status.
- Final traceability.

---

## Manual Workflow

Preparation follows this sequence:

```text
Capture Candidate
  -> Preserve Provenance
  -> Classify Sensitivity
  -> Identify Canonical Owner
  -> Review Freshness and Conflict
  -> Prepare Exact Proposed Change
  -> Define Validation and Traceability
  -> Human Decision
  -> STOP
```

Preparation stops before canonical application. Mission approval or permission to prepare a candidate is not candidate acceptance.

Only after a separately recorded `Accept` may the workflow continue:

```text
Apply to Canonical Owner
  -> Validate and Synchronize
  -> Preserve Final Traceability
```

Material changes to wording, evidence, scope, owner, or sensitivity require renewed review before application.

---

## Decision States

### Accept

Permits later bounded application of the exact reviewed proposal. Acceptance does not itself authorize application scope, commit, or push.

### Reject

Closes the candidate with an attributable rationale.

### Defer

Preserves the candidate with a reason and explicit revisit trigger or requested condition.

### Supersede

Records that another candidate or proposal replaces this one. It is a non-accepting transition.

### More Evidence

Returns the candidate for additional evidence or validation. It is a non-accepting transition.

### Redirect

Sends the candidate for review by a different proposed canonical owner or authority. It is a non-accepting transition.

For an important candidate, `Supersede`, `More Evidence`, and `Redirect` should remain under an explicit non-accepting disposition until the resulting proposal receives `Accept`, `Reject`, or `Defer`.

---

## Application Rules

- Apply a candidate only after an exact, human-reviewed `Accept` is recorded.
- Apply the accepted knowledge to one canonical owner.
- Have other documents reference the canonical owner rather than duplicate the durable rule.
- Obtain separate authorization for application scope, commit, and push.
- Do not expand authority automatically through application.
- Return material changes for renewed review.

---

## Validation and Synchronization

For repository knowledge, perform the following as relevant to the accepted destination and bounded application:

- Destination-specific review.
- Document registration.
- Generated-context regeneration.
- Tests.
- `git diff --check`.
- `./atlas validate`.
- `./atlas missing`.
- `./atlas docs` and `./atlas explain` when discovery changes.
- `./atlas sync`.
- `./atlas review`.
- Commit and push after separate authorization.
- Verification of a clean final repository state.

Validation provides evidence that an authorized application is correct. It does not accept the candidate or expand the accepted scope.

---

## Traceability

Preserve enough traceability to identify:

- The candidate considered.
- Its evidence and provenance.
- The decision authority and date.
- The disposition and rationale.
- The accepted destination, when applicable.
- The applied files and commit, when applicable.
- Validation evidence.
- Revisit conditions for a deferred candidate.

Retain a historical record only when its maintenance value justifies retention. Git may provide part of the trace, but it must not be claimed as evidence for details it does not preserve.

---

## Reusable Manual Template

```markdown
# <Candidate title or dated identifier>

- Authority class: <class>
- Canonical: No
- Generated: <Yes/No>
- Workflow status: <status>
- Candidate statement: <statement>
- Sources and provenance: <sources, transformations, and provenance>
- Producer: <human/tool/workflow/model when relevant>
- Dates and freshness: <dates and freshness boundary>
- Evidence summary: <supporting evidence>
- Evidence limitations: <limitations>
- Sensitivity: <classification>
- Retention and redaction boundary: <boundary>
- Confidence and uncertainty: <assessment>
- Proposed canonical owner: <one owner>
- Proposed destination section: <section>
- Existing canonical context: <context>
- Conflict and compatibility review: <review>
- Exact proposed change: <reviewable text or patch>
- Consequences and maintenance burden: <assessment>
- Validation plan: <checks>
- Required human authority: <authority>
- Decision record: <decision, authority, date, rationale>
- Application status: Not authorized
- Final traceability: <decision, destination, files, commit, and validation when known>

Human Decision: Unmade
Canonical Owner Changed: No
STOP — Await explicit human disposition before application.
```

---

## Completion Boundary

A single promotion flow is complete only when:

- Its disposition is explicit.
- Accepted changes are applied and verified, or a non-accepting disposition is preserved.
- Traceability is complete.
- Authority boundaries remain intact.
