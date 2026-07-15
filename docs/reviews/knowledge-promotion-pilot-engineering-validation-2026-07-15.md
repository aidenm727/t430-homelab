# Knowledge Promotion Pilot: Engineering Validation Gates

> **Authority class:** Candidate Finding supported by Execution Records
>
> **Canonical:** No
>
> **Generated:** No
>
> **Status:** Accepted and Applied
>
> **Date:** July 15, 2026
>
> **Procedure owner:** `docs/knowledge-promotion.md`
>
> **Proposed canonical owner:** `docs/standards/engineering-collaboration.md`
>
> **Decision authority:** Owner

## Candidate Statement

Repository automation and commit gates should validate stable machine-verifiable invariants structurally. They should not use brittle case-sensitive exact prose matching for human-reviewed documentation unless the exact wording itself is a declared contract.

## Provenance and Evidence

This candidate is based on direct owner-observed execution evidence from July 15, 2026.

Several discarded guarded commit-runner variants rejected an already reviewed six-file change because harmless editorial wording differed:

- “Capture the failed state” versus “capture failed state.”
- “Complete” versus lowercase “completed.”
- Capitalization of “Automatic model routing.”
- Prose describing omitted username/computer-name data being mistaken for raw private-field leakage.

Git independently preserves the successful final six-file integration and commit `f4081fc`, but does not independently preserve every discarded runner variant.

The underlying repository change had already passed human patch review, 43 tests, Atlas Valid, Atlas Missing, Atlas Synchronized, privacy review, exact-scope checks, and protected-branch checks.

The successful runner checked stable structural invariants, metadata, hashes, actual private literals, and raw-field syntax rather than editorial substrings.

## Evidence Limitations and Confidence

The discarded-runner details are owner-reported direct execution evidence. Git does not prove those exact discarded failures.

Confidence is **High** that brittle prose checks caused false negatives. The exact proposed standard wording was subject to human review and accepted by the owner.

## Sensitivity, Retention, and Redaction Boundary

This record contains Ordinary Personal engineering context and uses a sanitized summary.

Private diagnostic literals, the Windows username, computer name, email address, raw diagnostic logs, and unnecessary transcript dumps are excluded. The record should retain only the evidence needed to review the candidate and preserve its later disposition.

## Producing Roles and Workflow

- Candidate Producer: owner, based on direct execution observation.
- Workflow Operator / Record Custodian: Codex, within the bounded Stage 2 repository implementation.
- Proposed Canonical Owner: Engineering Collaboration Contract.
- Human Decision Authority: owner.
- Implementer: Codex, within the separately scoped Stage 3 canonical application.
- Verifier: Codex, using the bounded Stage 3 validation plan under owner authority.

## Dates and Freshness

The execution evidence, candidate, decision, and bounded application are current as of July 15, 2026. Re-review freshness if later tooling, repository conventions, or canonical standards materially change.

## Existing Canonical Context

The Engineering Collaboration Contract already prioritizes deterministic, low-friction, verifiable workflows. It also says recurring workflow friction should be classified and integrated when worth solving.

This candidate narrows how validation gates should divide machine checks from human editorial review. It must not weaken checks for hashes, paths, schemas, metadata, branch identities, actual private literals, secrets, or explicitly declared literal contracts.

## Conflict and Compatibility Review

- No known canonical rule requires exact phrase matching for ordinary prose.
- Exact checks remain necessary for true literal contracts.
- Human review remains responsible for editorial meaning.
- A pseudo-semantic prose matcher must not substitute for human review.
- The proposal is compatible with deterministic verification only if structural and literal-contract checks remain strong.

## Exact Proposed Standard Change

The following exact proposed subsection is preserved in this pilot and was accepted and applied to the proposed canonical owner without materially changed wording.

### Validation Gate Standard

Repository automation and commit gates should validate stable, machine-verifiable invariants structurally.

Exact checks are appropriate for declared contracts such as paths, hashes, metadata values, branch identities, schemas, and explicitly required literals. Human-reviewed documentation prose should not be gated by case-sensitive exact phrase matching unless the exact wording itself is a declared contract.

For editorial documentation, deterministic gates should check available structure and metadata, while human patch review owns wording and meaning. Privacy gates should detect actual private literals or raw-field syntax, not infer leakage from ordinary prose that describes redaction or omission.

When a semantic requirement cannot be expressed as a stable structural invariant, record it as a human-review criterion rather than simulating semantic validation with brittle prose matching.

## Application Destination

- Canonical owner: `docs/standards/engineering-collaboration.md`.
- Applied placement: a new subsection under `Implementation Artifact Standard`, before the next unrelated major section.

## Consequences and Maintenance Burden

The accepted proposal makes the division between deterministic gate checks and human editorial review explicit. It requires future gate authors and reviewers to identify declared literal contracts and avoid editorial-substring checks that create false negatives.

The maintenance burden is limited to keeping the standard aligned with actual repository validation practices and re-reviewing it if reliable structural checks or declared contracts change.

## Validation Plan After Accept

- Apply only the exact accepted wording or return for renewed review.
- Run `git diff --check`.
- Run the tests.
- Run Atlas validate, missing, sync, and review.
- Regenerate generated context only if a canonical generated source changes.
- Verify that no unrelated files changed.
- Preserve decision and commit traceability.

## Human Authority Boundary

The owner explicitly accepted the exact proposed text on July 15, 2026, permitting only a separately scoped application stage. The decision did not authorize automatic promotion, unrelated editorial changes, authority expansion, commit, push, or mutation of EO-2026-020.

## Decision Record

- Decision: Accept
- Decision authority: Owner
- Decision date: July 15, 2026
- Rationale: Owner accepted the exact proposed text without supplying additional rationale.
- Canonical application: Separately scoped and applied.
- Engineering Collaboration Contract changed: Yes, with the exact accepted subsection and no materially changed wording substituted.

## Application Status and Traceability

The exact accepted text was applied to `docs/standards/engineering-collaboration.md` in the separately scoped Stage 3 canonical change. No materially changed wording was substituted. Validation was performed across exact text, generation, formatting, privacy, tests, Atlas state, forbidden files, repository scope, and protected refs.

This pilot preserves the original candidate, sanitized evidence, limitations, conflict review, exact proposal, human decision, bounded application, and validation. EO-2026-020 remains reviewed. No automatic promotion or authority expansion occurred.

The Accept decision did not itself authorize commit or push. Commit and push remain separately controlled actions. The repository commit that introduces the accepted standard and this pilot record supplies the final commit identity and Git traceability. No commit SHA is hard-coded before that commit exists.

Accepted and Applied — Repository traceability is supplied by the commit that introduces this record.
