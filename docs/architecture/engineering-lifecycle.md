# Engineering Lifecycle Architecture

## Purpose

The Engineering Lifecycle defines how an authorized checkpoint becomes a
verified candidate, receives required review and owner decisions, and may later
be published or deployed. It makes corrections efficient without weakening
scope, evidence, or authority boundaries.

## Core Principle

Focused verification supports implementation. One tier-appropriate broad check
establishes the final candidate only after the last in-scope mutation.

## Lifecycle Flow

    Accepted brief and bounded implementation authority
        ↓
    Environment preflight
        ↓
    Implement with focused verification
        ↓
    Document, generate, validate, and synchronize
        ↓
    Final broad/native verification after the last mutation
        ↓
    Required independent review
        ↓
    Bounded correction and renewed final evidence when needed
        ↓
    Explicit owner acceptance
        ↓
    Separately authorized publication or deployment

Repository state, Atlas guidance, verification, and review report facts; none
of them silently advances another lifecycle gate or grants authority.

## Verification Sequencing

Focused tests run when a useful baseline exists, after coherent increments,
and after each correction against the affected behavior and nearby regression
boundary. They are not rerun merely because work changes hands or a report is
rewritten.

Final broad verification is proportional:

- Tier 1 uses the smallest appropriate broad check; a repository-wide suite is
  required only for shared behavior or test infrastructure.
- Tier 2 uses one final capability-wide or repository-wide native suite chosen
  in the checkpoint brief.
- Tier 3 uses one final full appropriate native suite, including relevant
  adversarial or negative paths.

The recorded final run must follow the final repository mutation. Any later
mutation invalidates that run as final evidence for the resulting tree. When a
review causes corrections, group them, use focused tests while correcting, and
run the broad suite once after the last correction.

Synthetic selected, idle, and error fixtures must be isolated from mutable live
state. A canonical file or live data root may be used only when an explicitly
named smoke or authorized live verification is the subject.

## Correction Continuation

A correction continues within the checkpoint without restarting design or
authorization only when all of these remain unchanged:

- goal and observable result;
- risk tier and accepted architecture;
- authorized paths and operations;
- data, dependency, configuration, external-target, and protected boundaries;
  and
- rollback, verification, and stop conditions.

After an in-scope correction, rerun affected focused checks. Tier 2 review
confirms a material affected delta. A Tier 3 blocking correction requires a
fresh final adversarial review after final verification.

Stop for an owner decision when authority is ambiguous, a protected boundary
is approached, or a material alternative or tradeoff appears. Redesign or open
a new checkpoint when scope, tier, architecture, dependency, configuration,
external target, protected boundary, or observable result changes, or when
rollback or verification is no longer bounded.

## Anti-Loop Stops

Stop rather than begin an uncontrolled correction cycle when:

- the same defect class remains or returns after two correction attempts;
- a third correction cycle would be required;
- scope, tier, dependency, configuration, external target, or a protected
  boundary expands;
- architecture and implementation conflict;
- evidence cannot truthfully identify the candidate or its verification;
- verification cannot run in an accepted environment; or
- the owner can no longer explain the goal, current state, risk, or next
  decision.

## Responsibilities

The lifecycle preserves architecture, generated ownership, repository
validation and synchronization, complete-diff inspection, finding disposition,
and human-controlled mission advancement. Atlas may observe and recommend; the
owner approves direction, acceptance, publication, deployment, and external
writes.

## Non-Responsibilities

The lifecycle does not replace human judgment, treat generated context as
canonical, hide uncertainty, infer authority, auto-advance missions, or require
repeated full-suite runs without a new final candidate.
