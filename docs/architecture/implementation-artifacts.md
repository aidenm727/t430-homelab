# Implementation Artifacts Architecture

## Purpose

Implementation Artifacts define how engineering intent becomes safe, reviewable, executable change material.

This architecture exists because implementation output is part of the engineering system.

An implementation artifact is not complete merely because its content is correct.

It must also be generated, transported, validated, delivered, executed, reviewed, verified, and documented safely.

---

## Core Principle

Implementation artifacts are first-class engineering workflow objects.

The Aiden Platform should not depend on fragile conversational formatting for meaningful engineering changes.

Artifact generation and delivery should become increasingly deterministic, validated, and Atlas-aware.

---

## Architectural Position

Implementation Artifacts support the Engineering capability of the Aiden Platform.

    Engineering Intent
        ↓
    Implementation Artifact Generation
        ↓
    Artifact Transport
        ↓
    Artifact Validation
        ↓
    Artifact Delivery
        ↓
    Repository Change
        ↓
    Verification
        ↓
    Documentation
        ↓
    Commit

Artifact work sits between design decisions and repository changes.

---

## Artifact Generation

Artifact Generation determines what implementation artifact should be produced.

It includes:

    - understanding the requested change
    - estimating artifact complexity
    - selecting the safest transport
    - deciding whether full replacement, section replacement, patching, or commands are appropriate
    - preparing verification commands
    - checking whether the artifact is likely to survive delivery

Generation must happen after transport selection, not before it.

---

## Artifact Transport

Artifact Transport defines how an artifact moves from AI-assisted engineering into the terminal or repository.

Transport options include:

    - direct shell commands
    - shell heredoc
    - Python writer
    - patch file
    - generated file
    - future Atlas apply-style workflow

Artifact Transport is defined in:

    docs/architecture/artifact-transport.md

---

## Artifact Validation

Artifact Validation checks whether the generated artifact is safe to deliver.

Validation should check:

    - transport choice
    - formatting risk
    - nested Markdown fence risk
    - escaping risk
    - copy-paste reliability
    - whether the artifact is one contiguous executable block
    - whether verification commands are included

If validation fails, the artifact must be regenerated or escalated to a safer transport.

---

## Artifact Delivery

Artifact Delivery defines the final user-facing implementation output.

Delivery should include:

    - one contiguous implementation artifact
    - exact verification commands
    - the next engineering checkpoint

During implementation-focused sessions, delivery should minimize explanation and maximize safe execution.

---

## Transport Selection Algorithm

Implementation artifacts should use this decision order:

    1. If the change is a small set of terminal operations, use direct shell commands.
    2. If the change writes a small simple text file, use a shell heredoc.
    3. If the change writes Markdown longer than a short note, use a Python writer.
    4. If the change writes Markdown containing code examples, use a Python writer.
    5. If the change is escaping-sensitive, use a Python writer.
    6. If the change modifies a precise portion of an existing file, use a patch or Python targeted replacement.
    7. If the change spans multiple files, prefer a Python writer or future Atlas apply-style workflow.
    8. If transport validation fails, escalate to a safer transport before delivery.

For architecture documents, Python writer is the default unless the document is very small and contains no formatting-sensitive content.

---

## Markdown Safety Rule

Markdown documents are formatting-sensitive artifacts.

When a Markdown document is delivered through a shell heredoc, the generated Markdown must not contain fenced code blocks.

Use four-space indented code blocks instead.

For Markdown-heavy architecture documents, avoid heredoc transport and use a Python writer.

---

## Relationship to Engineering Collaboration

The Engineering Collaboration Contract defines the human-AI workflow.

Implementation Artifacts define the implementation-output lifecycle inside that workflow.

The collaboration contract should rely on this architecture for artifact generation, transport, validation, and delivery standards.

---

## Relationship to Atlas

Atlas should eventually understand implementation artifacts as part of engineering workflow readiness.

Future Atlas capabilities may:

    - recommend artifact transport
    - validate generated artifacts
    - stage changes before application
    - apply structured artifacts
    - detect formatting and transport risks
    - provide artifact templates
    - verify artifact completion criteria

Workflow rules should be written so Atlas can eventually reason about them.

---

## Non-Responsibilities

Implementation Artifacts should not:

    - replace architectural judgment
    - bypass human review
    - bypass repository validation
    - bypass verification
    - encourage blind execution
    - store secrets
    - become a general writing style guide

---

## Completion Criteria

This architecture is established when:

    - implementation artifacts have a documented lifecycle
    - artifact generation is separated from transport
    - artifact transport is documented separately
    - artifact validation is required before delivery
    - engineering collaboration references this architecture
    - Atlas metadata recognizes the architecture

---

## Future Direction

Implementation Artifacts should evolve toward repository-native, Atlas-validated engineering change delivery.

The long-term goal is to replace fragile copy-paste workflows with deterministic artifact generation, validation, staging, application, verification, and documentation.
