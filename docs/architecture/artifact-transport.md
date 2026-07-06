# Artifact Transport Architecture

## Purpose

Artifact Transport defines how implementation artifacts are safely moved from AI-assisted engineering into the terminal or repository.

Its purpose is to prevent formatting, escaping, rendering, and copy-paste failures from interrupting engineering work.

Recurring artifact failures are engineering workflow failures, not isolated chat mistakes.

---

## Core Principle

Artifact transport must be selected deliberately.

The chosen transport must preserve the artifact through delivery, copy, paste, execution, review, and verification.

Transport correctness takes priority over brevity.

---

## Scope

Artifact Transport owns the delivery mechanism.

It does not own the full artifact lifecycle.

The parent lifecycle is defined in:

    docs/architecture/implementation-artifacts.md

Artifact Transport is responsible for:

    - shell command transport
    - heredoc transport
    - Python writer transport
    - patch transport
    - future Atlas apply-style transport
    - transport safety rules
    - transport escalation rules

---

## Transport Options

Supported transport options include:

    1. Direct shell commands
    2. Shell heredoc
    3. Python writer
    4. Patch file
    5. Generated file
    6. Future Atlas apply-style workflow

---

## Direct Shell Commands

Use direct shell commands for simple terminal operations.

Appropriate examples:

    - creating directories
    - running validation commands
    - moving files
    - simple Git inspection
    - short deterministic edits

Direct shell commands should remain short, obvious, and easy to review.

---

## Shell Heredoc

Use shell heredoc for small simple text files.

Do not use heredoc when the generated content is long, Markdown-heavy, escaping-sensitive, or likely to contain nested formatting.

When writing Markdown through heredoc:

    Do not use fenced code blocks inside the generated Markdown.

Use four-space indented code blocks instead.

---

## Python Writer

Use a Python writer for:

    - architecture documents
    - long Markdown files
    - Markdown files containing examples
    - escaping-sensitive content
    - multi-file documentation changes
    - targeted replacement in existing files
    - artifacts where transport failure would halt progress

For architecture documents, Python writer is the default transport.

---

## Patch Files

Use patch files for precise diffs when full replacement is unnecessary.

Patch transport is useful when:

    - the target file is large
    - only a small section should change
    - preserving surrounding content matters
    - reviewability is more important than full rewrite simplicity

---

## Future Atlas Apply Transport

Atlas should eventually support structured artifact application.

Future Atlas apply-style workflows may:

    - stage changes
    - validate expected file paths
    - validate document metadata
    - apply patches
    - reject unsafe artifacts
    - produce verification commands
    - preserve an artifact application record

---

## Transport Escalation

If a selected transport creates formatting, escaping, rendering, or copy-paste risk, escalate to a safer transport before delivery.

Default escalation path:

    Shell heredoc
        ↓
    Python writer
        ↓
    Patch or future Atlas apply workflow

Do not ship an artifact after transport validation has failed.

---

## Relationship to Implementation Artifacts

Implementation Artifacts define the full lifecycle.

Artifact Transport defines the movement mechanism inside that lifecycle.

    Implementation Artifact Generation
        ↓
    Artifact Transport
        ↓
    Artifact Validation
        ↓
    Artifact Delivery

---

## Relationship to Engineering Collaboration

The Engineering Collaboration Contract should use Artifact Transport rules when producing implementation artifacts.

During implementation-focused sessions, ChatGPT should choose transport deliberately and validate that choice before delivery.

---

## Non-Responsibilities

Artifact Transport should not:

    - decide engineering priority
    - replace implementation design
    - replace artifact validation
    - bypass human review
    - bypass verification
    - store secrets
    - become a general Markdown style guide

---

## Completion Criteria

This architecture is established when:

    - transport options are documented
    - heredoc limits are explicit
    - Python writer defaults are explicit
    - transport escalation is defined
    - implementation artifacts reference transport as a sub-capability
    - engineering collaboration uses these rules

---

## Future Direction

Artifact Transport should become a deterministic, Atlas-aware capability for safely moving implementation changes into the repository.

The long-term goal is for Atlas to recommend, validate, and eventually apply artifacts using explicit transport rules instead of relying on fragile manual copy-paste behavior.
