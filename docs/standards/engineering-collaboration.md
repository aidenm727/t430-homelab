# Engineering Collaboration Contract

## Purpose

This document defines how the human engineer, Atlas, ChatGPT, and the repository collaborate to evolve the Aiden Platform.

Its purpose is to make engineering sessions deterministic, low-friction, verifiable, and aligned with platform architecture.

`AGENTS.md` is the primary repository-local authority-interpretation contract.
This standard governs collaboration behavior beneath that contract and may not
create or expand authority.

## Core Principle

AI assistance should increase engineering agency, not replace judgment or create confusion.

No implementation-focused engineering work should begin until live engineering state has been established.

Engineering session startup is defined by:

    docs/architecture/engineering-sessions.md

## Responsibilities

The human engineer owns goals, judgment, execution, verification, review, commits, and final decisions.

The repository preserves canonical engineering truth through architecture, infrastructure records, operations history, roadmaps, standards, generated context, and engineering tools.

Atlas provides deterministic engineering awareness from the repository and working tree.

ChatGPT assists with architecture, planning, explanation, documentation, and implementation artifacts.

## Relationship to Engineering Sessions

Session startup, session readiness, source-of-truth order, and Atlas bootstrap architecture are defined by:

    docs/architecture/engineering-sessions.md

This contract does not replace session architecture.

It defines how ChatGPT should collaborate with the human engineer and Atlas once session context is established.

## Deliberate Engineering Work

Repository understanding begins once enough state is known to work
deliberately. Understanding, a healthy repository, selected work, Atlas output,
and writable tools do not establish task or implementation authority.

Lifecycle:

    Understand
    Classify and Brief
    Design
    Accept Design
    Implement
    Verify
    Review
    Accept Candidate
    Authorize Publication or Deployment

Explicit current owner instruction establishes task authority. Implementation
authority must be separately explicit and bounded. Publication, deployment, and
external writes remain separately explicit.

Ordinary work may continue without repeated approval inside an already
authorized exact checkpoint and its stop conditions. Casual continuation or
acknowledgment language may continue that existing authority, but it may not:

- select a new checkpoint;
- convert review, analysis, diagnosis, inventory, or design into implementation;
- expand writable paths, capabilities, or external targets;
- override a stop condition;
- establish actor authorization; or
- authorize publication, deployment, or any external write.

Pause when an owner decision is required, authority or live state is missing,
verification fails materially, documentation conflicts cannot be resolved
within the accepted design, or the authorized boundary must expand.

## Engineering Workflow v1.1

Workflow v1.1 scales assurance by potential consequence, not by line count or
file count. Any Tier 3 trigger makes the checkpoint Tier 3. Mixed work uses the
highest applicable tier unless lower-consequence work can be cleanly separated
into its own checkpoint, authority, and evidence. Unresolved consequence or
boundary uncertainty moves work up one tier or stops for owner decision.

### Tier 1 — Routine

Tier 1 requires all consequences to be local, reversible, and low blast radius,
with no canonical-state, authority, security, privacy, identity, access,
secret, protected-reference, live-data, destructive, migration, dependency, or
material cross-component consequence.

The checkpoint brief is the design by default and may remain in the current
owner instruction or handoff. Independent review is not automatic. Use focused
verification and the smallest appropriate broad check; use the repository-wide
suite only when shared behavior or test infrastructure changes. In-scope
corrections continue. Publication and deployment remain separately explicit.

### Tier 2 — Material Capability

Tier 2 applies to a meaningful user workflow, persisted non-sensitive data
behavior, public interface, operational behavior, bounded reversible runtime,
dependency, or configuration change, or a cross-component contract, provided
no Tier 3 trigger applies.

Use a concise design decision covering affected interfaces, data, rollback,
and material alternatives. The owner explicitly accepts that design and the
implementation boundary. Run focused and native capability checks, then one
final capability-wide or repository-wide native suite after the last mutation.
One fresh independent review of the exact final candidate is required by
default, followed by explicit owner acceptance. Publication and deployment
remain separately explicit.

### Tier 3 — High Consequence

Tier 3 applies to canonical-state or authority semantics; security, privacy,
identity, access, secrets, or protected material; destructive or irreversible
operations; live-data migration; recovery guarantees; broad foundation or
platform contracts; high-impact external actions; or material public identity
or privacy consequences.

Use targeted architecture and applicable risk, abuse, privacy, migration,
rollback, or recovery analysis. Research occurs only when existing evidence is
insufficient. Explicit design acceptance precedes tightly bounded
implementation authority naming paths, protected operations, data boundaries,
and stop conditions. Final verification includes focused and full appropriate
native coverage after the last mutation and relevant adversarial or negative
paths. One adversarial independent review is required, with a fresh final review
after blocking corrections, followed by explicit owner acceptance and tightly
bounded external authority.

Classification checks do not select work: F1 is Tier 3; an isolated synthetic
documentation-link correction is Tier 1; R1 is Tier 3; and S1 is Tier 2 with
separately bounded Tier 3 sub-boundaries for credentials, private access,
destructive storage, migration, or recovery-critical operations. R1 and S1 are
examples only until explicitly selected and authorized.

### Checkpoint Brief

Use one concise Markdown block with exactly these fields:

- **Why:** Owner value and the problem being solved.
- **Risk tier:** The tier and consequence-based trigger.
- **Exact scope:** Authorized capabilities, paths, data, and targets.
- **Exclusions:** Excluded paths, operations, dependencies, systems, and
  follow-on work.
- **Authority established:** Task, implementation, local commit when
  applicable, acceptance, publication, and deployment stated separately.
- **Protected boundaries:** Secrets, protected references, private/live data,
  live systems, generated ownership, and unrelated user changes.
- **Observable result:** What a human can inspect or do afterward.
- **Verification:** Focused checks, final broad/native check, review
  requirement, and evidence location.
- **Stop conditions:** Checkpoint-specific and shared anti-loop conditions.
- **Next decision boundary:** The exact owner decision required after the
  current lifecycle state.

A brief describes authority but never creates it. Its authority field cites the
explicit current owner boundary. Tier 1 creates no repository file by default.
Tier 2 and Tier 3 open one ordinary dated `docs/reviews/` evidence record and
append lifecycle facts to that record or its compound evidence rather than
creating parallel planning reports.

### Separate Authority and Acceptance Gates

- Explicit owner selection establishes task authority only.
- Design acceptance approves the design only unless implementation authority
  is separately explicit in the same owner instruction.
- Implementation authority names the exact capability, paths, data, targets,
  and protected operations; it does not authorize acceptance or external
  action.
- Verification and independent review establish evidence and findings, not
  owner acceptance.
- Owner acceptance applies only to the exact verified and reviewed candidate.
- Staging, local commits and ref changes, publication, deployment, migration,
  destructive operations, and every external write require separately explicit
  authority naming their exact targets and modes.

Silence does not accept. A Tier 1 owner may combine outcome acceptance with a
separately explicit publication decision, but the two facts must remain clear.

### Environment and Verification Contract

Before the first mutation and native verification, establish the repository and
execution environment defined in
`docs/architecture/engineering-sessions.md`. Record checkpoint-specific roots,
restrictions, and commands in the brief. Do not probe unauthorized data or
protected paths.

Use focused checks before mutation when useful, after coherent increments, and
after corrections. Final broad verification follows the last mutation at the
tier defined above; any later mutation invalidates it as final evidence. Do not
repeat a full suite merely because work changes hands or documentation is
rewritten. Synthetic selected, idle, and error behavior uses isolated fixtures;
live canonical files or data roots are limited to explicitly identified smoke
or authorized live checks.

`docs/architecture/engineering-lifecycle.md` owns correction continuation,
verification sequencing, and anti-loop stops.

### Compact Compound Evidence

Tier 2 and Tier 3 preserve one compound durable bundle:

1. One dated ordinary Markdown record under `docs/reviews/`.
2. Immutable Git history for candidate and published identities and exact
   changed paths once commits are separately authorized.
3. A stable publication or deployment attestation when final facts occur after
   the repository commit.

The Markdown record preserves the accepted brief, preflight outcome, final
changed paths, verification command/result anchors, independent findings and
disposition, owner acceptance and boundary, publication/deployment authority
and boundary, correction cycles, and stop assessment. Before commit it names
the base and explicitly describes the candidate as uncommitted; it never
invents a future identity or external result.

Prompts, full chats, source transcripts, temporary reports, and every
intermediate test run are not durable dependencies. Later reviewers should be
able to reconstruct the boundary, decisions, candidate, and result from the
compact record, Git, and any cited durable attestation.

One coherent commit is the publication default. A narrow second commit is
justified only when a canonical record must cite an identity that cannot exist
before the first commit, owner acceptance or final external results must be
repository-owned, or canonical state can transition only after the accepted
candidate identity exists. Convenience, formatting, or routine documentation
does not justify it.

### Publication and Deployment Procedure

For every tier:

1. Confirm the exact accepted candidate, required finding disposition, and
   final verification after its last mutation.
2. Confirm generated files derive from authorized canonical sources and are
   synchronized.
3. Inspect the complete diff and changed-path list against the brief.
4. Obtain separate authority naming exact staging paths, local ref mutation,
   remote ref or deployment target, mode, and prohibited actions.
5. Stage only authorized paths and verify the staged boundary.
6. Create the minimum coherent commit or commits and record immutable identity.
7. Perform only the exact authorized non-force push or deployment action.
8. Verify local, tracking, remote, or deployment alignment to the degree the
   authorized action permits.
9. Verify a clean worktree, generated synchronization, and preservation of
   unrelated paths.
10. Complete the durable attestation and owner-facing status.

### Atlas Boundary

Workflow v1.1 adds no Atlas feature, command, schema, or simulated semantic
judgment. Atlas continues to observe deterministic repository facts. A generic
preflight helper is eligible only after at least two real checkpoints reproduce
stable checks worth automating; an Atlas change additionally requires a
recurring machine-verifiable gap that existing commands or concise preflight
cannot address and a concrete near-term consumer.

## Implementation Artifact Standard

Implementation artifacts should prioritize low-friction terminal execution.

During implementation-focused sessions, the default response should provide one copy-pasteable terminal-native artifact unless the user explicitly requests another format.

Preferred formats:

1. Terminal-native command block
2. Complete file replacement
3. Complete section replacement
4. Exact verification command sequence

Manual editing should be the fallback, not the default.

ChatGPT should choose the safest transport format for the artifact size and complexity.

Default transport guidance:

1. Use shell commands for simple changes.
2. Use heredoc file replacement only for simple text files.
3. Use Python writers for large, brittle, Markdown-heavy, or escaping-sensitive documents.
4. Use patch files for precise diffs when full replacement is unnecessary.
5. Use future Atlas apply-style artifacts when structured repository artifact application exists.

Implementation artifact generation, transport, validation, and delivery are defined architecturally by:

    docs/architecture/implementation-artifacts.md
    docs/architecture/artifact-transport.md

Terminal-native artifacts must avoid nested Markdown fences.

When generating Markdown files through shell heredocs, do not use fenced code blocks inside the generated Markdown.

Use four-space indented code blocks instead.

Before sending an implementation artifact, ChatGPT must perform artifact preflight:

1. Identify the transport mechanism.
2. Determine whether the artifact writes Markdown.
3. Check whether nested fenced code blocks would be created.
4. Escalate to a Python writer when Markdown formatting risk exists.
5. Default to Python writers for architecture documents unless the document is very small and formatting-safe.
6. Include exact verification commands.

Transport correctness takes priority over artifact brevity.

### Validation Gate Standard

Repository automation and commit gates should validate stable, machine-verifiable invariants structurally.

Exact checks are appropriate for declared contracts such as paths, hashes, metadata values, branch identities, schemas, and explicitly required literals. Human-reviewed documentation prose should not be gated by case-sensitive exact phrase matching unless the exact wording itself is a declared contract.

For editorial documentation, deterministic gates should check available structure and metadata, while human patch review owns wording and meaning. Privacy gates should detect actual private literals or raw-field syntax, not infer leakage from ordinary prose that describes redaction or omission.

When a semantic requirement cannot be expressed as a stable structural invariant, record it as a human-review criterion rather than simulating semantic validation with brittle prose matching.

## Formatting Standard

During implementation-focused engineering sessions, ChatGPT should optimize formatting for engineering execution rather than conversational presentation.

Engineering output should be easy to copy, paste, run, verify, and review.

Avoid:

- fragile nested Markdown formatting
- multiple disconnected snippets when one block would work
- mixing explanation, file content, and verification inside one confusing artifact
- executable commands for unverified future capabilities
- decorative formatting that makes terminal execution harder

Prefer:

- one clean terminal-native block per implementation step
- exact verification commands
- clear file paths
- explicit next checkpoints
- repository-supported commands

## Workflow Calibration

Recurring collaboration friction should be treated as an engineering problem.

When friction is observed during implementation-focused work, ChatGPT should classify it immediately:

1. Implement now.
2. Capture for later.
3. Discard as not worth solving.

If the decision is implement now, ChatGPT should provide one terminal-native implementation artifact.

If the decision is capture for later, ChatGPT should briefly state where the idea belongs and then continue the active engineering work.

If the decision is discard, ChatGPT should briefly explain why and continue the active engineering work.

ChatGPT should not repeatedly discuss a principle without deciding whether it will be implemented, captured, or discarded.

During workflow calibration sessions:

- recurring issues should be classified against the active checkpoint and
  integrated only when the accepted scope and implementation authority include
  this contract,
- improvements should be documented as engineering refinements,
- the objective is to improve future engineering sessions rather than merely complete the current task.

## Completion Standard

Implementation handoffs should state the exact candidate outcome, verification,
unresolved risk, lifecycle state, and next owner decision. The compact
owner-facing format is defined in `docs/architecture/engineering-review.md`.

## Long-Term Direction

This contract should make future engineering sessions easier to start, verify, continue, and transfer across chats.

The long-term goal is for Atlas and the repository to provide enough
deterministic context for deliberate repository understanding and bounded
execution with minimal conversational setup while preserving human judgment
and architectural discipline. Repository context, repository health, selected
work, and Atlas output do not establish current task, implementation, or
publication authority.
