# Engineering Collaboration Contract

## Purpose

This document defines how the human engineer, Atlas, ChatGPT, and the repository collaborate to evolve the Aiden Platform.

Its purpose is to make engineering sessions deterministic, low-friction, verifiable, and aligned with platform architecture.

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

## Engineering Mode

Engineering Mode begins once enough state is known to work deliberately.

Lifecycle:

    Understand
    Design
    Accept Decision
    Implement
    Verify
    Document
    Synchronize
    Commit
    Push

Once Engineering Mode has begun, conversational acceptance phrases authorize progress to the next engineering checkpoint.

Examples:

- let's do it
- go ahead
- continue
- sounds good
- yep
- okay

ChatGPT should pause only when an architectural decision is required, live state is missing, verification fails, documentation conflicts exist, or genuine user input is required.

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

- recurring issues should be integrated into this contract before continuing,
- improvements should be documented as engineering refinements,
- the objective is to improve future engineering sessions rather than merely complete the current task.

## Completion Standard

Implementation responses should conclude with only:

    Verify
    Next

Verify contains exact checks.

Next identifies the next engineering checkpoint.

## Long-Term Direction

This contract should make future engineering sessions easier to start, verify, continue, and transfer across chats.

The long-term goal is for Atlas and the repository to provide enough deterministic context that ChatGPT can enter Engineering Mode with minimal conversational setup while preserving human judgment and architectural discipline.
