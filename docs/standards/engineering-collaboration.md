# Engineering Collaboration Standard

## Purpose

This document defines how AI-assisted engineering sessions should be conducted for the Aiden Platform.

Its purpose is to reduce friction, preserve engineering judgment, and make implementation work easier to copy, verify, document, commit, and continue.

## Core Principle

AI assistance should improve engineering agency, not create confusion.

Engineering responses should be clear, copy-safe, verifiable, and aligned with the platform architecture.

## Default Response Structure

During implementation sessions, AI engineering responses should normally use this structure:

1. Why
2. Change
3. Verify
4. Next

## Copy-Safe Implementation Rule

When providing repository-ready documentation, scripts, commands, or code, the primary artifact must be directly copyable.

The assistant must not use nested markdown code fences inside a copyable artifact.

If an inserted document needs to show an example command, file path, or output, use indented text instead of nested fences.

## Implementation Scope

Prefer one complete implementation artifact over scattered fragments.

For large files, provide one complete section replacement rather than many small edits.

Avoid making the user reconstruct a change from multiple partial snippets.

## Architecture Before Implementation

Before implementation, identify the relevant platform capability and determine whether architecture or standards need to change first.

Implementation should reinforce architecture rather than bypass it.

## Verification Requirement

Every meaningful implementation response should include exact verification commands.

Verification should check the thing that changed, not just confirm that a command ran.

## Documentation Responsibility

Meaningful engineering changes should be documented immediately after verification.

Generated context should summarize canonical documentation but never replace it.

## Ambiguity Handling

Pause and ask for clarification when:

- An architectural decision is genuinely unresolved
- Verification fails
- Documentation conflicts exist
- User input is required to avoid guessing

Otherwise, continue toward the next responsible engineering checkpoint.

## Formatting Standard

Engineering output should minimize copy/paste friction.

Avoid:

- Nested markdown fences inside copyable artifacts
- Multiple disconnected snippets when one block would work
- Decorative formatting that makes terminal or editor paste unreliable
- Ambiguous placeholders that require unnecessary manual repair

Prefer:

- One contiguous copyable block
- Plain markdown
- Indented examples inside markdown documents
- Explicit verification commands
- Clear next checkpoints

## Atlas Integration Direction

Atlas should eventually understand this standard as repository knowledge.

Future Atlas capabilities may validate whether repository changes, generated context, or engineering workflows follow documented standards.

This standard should become part of the platform's deterministic engineering context rather than remaining only a conversational preference.
