# Repository Reasoning Architecture

## Purpose

This document defines how repository reasoning works within the Aiden Platform engineering environment.

Atlas is the primary interface to repository reasoning.

The Repository Knowledge Layer allows Atlas to understand what exists within the repository.

The Repository Reasoning Layer builds on that knowledge by evaluating relationships, identifying engineering implications, and producing deterministic guidance for engineering work.

The reasoning layer does not replace engineering judgment.

It exists to make repository knowledge actionable.

---

## Architectural Position

The engineering stack is organized into four conceptual layers:

    Repository
        ↓
    Repository Knowledge Layer
        ↓
    Repository Reasoning Layer
        ↓
    Engineering Interface

The repository is the canonical engineering record.

The knowledge layer understands repository entities and metadata.

The reasoning layer evaluates relationships and implications.

The engineering interface exposes reasoning through commands, AI workflows, and future tools.

---

## Repository Knowledge

The Repository Knowledge Layer answers questions such as:

- What documents exist?
- Which repository layer does each document belong to?
- Is a document canonical or generated?
- Which capability does a document support?
- Which documents are related?
- Which documents are generated from other documents?
- Which tool manages a generated artifact?

Knowledge describes the repository without making engineering conclusions.

---

## Repository Relationships

Repository knowledge becomes useful when Atlas understands relationships between engineering entities.

Important relationships include:

- Architecture documents define platform intent.
- Capability documents define what the platform should be able to do.
- Infrastructure records describe current implementation.
- Operations records describe how changes were made.
- Roadmaps describe possible future improvements.
- Generated artifacts summarize canonical sources.
- Engineering tools operate on repository knowledge.
- Documents reference and depend on one another.

Repository reasoning operates primarily over these relationships rather than over isolated files.

Relationships should be represented once and reused by all reasoning capabilities.

---

## Repository Reasoning

The Repository Reasoning Layer consumes repository knowledge and produces engineering conclusions.

Reasoning should answer questions such as:

- What may be affected if this document changes?
- Which generated artifacts may need regeneration?
- Which related documents should be reviewed?
- Which repository rules may apply?
- What engineering actions are recommended?
- What is the next useful engineering checkpoint?
- What needs validation before work continues?

Reasoning should remain deterministic and explainable.

Every recommendation should be traceable back to repository knowledge.

---

## Reasoning Capabilities

The reasoning layer should evolve as a set of shared reasoning capabilities.

These capabilities are not commands.

Commands are interfaces that render reasoning results.

### Impact

Impact reasoning answers:

- What changes if this repository entity changes?
- Which related documents should be reviewed?
- Which generated artifacts may be affected?
- What follow-up actions are likely needed?

Initial interface:

- atlas impact

### Guidance

Guidance reasoning answers:

- What should happen next?
- Is the repository ready for new work?
- What documents are most relevant to the current checkpoint?
- What commands should be run next?

Initial interface:

- atlas next

Future interfaces may include:

- atlas state
- atlas plan

### Validation

Validation reasoning should answer:

- Is the repository internally consistent?
- Are required documents present?
- Do discovered documents have metadata definitions?
- Are generated artifacts marked correctly?
- Are repository layering rules being followed?
- Are known source-of-truth rules being respected?

Future interface:

- atlas validate

### Synchronization

Synchronization reasoning should answer:

- What changed?
- What generated artifacts may need regeneration?
- What AI context may be stale?
- What documentation should be reviewed after a change?
- What commands should synchronize the engineering environment?

Future interface:

- atlas sync

### Planning

Planning reasoning should answer:

- What sequence of work makes the most sense?
- Which capability is being improved?
- Which architecture should be reviewed before implementation?
- What verification and documentation steps should follow?

Future interfaces may include:

- atlas plan
- atlas roadmap

---

## Engineering Interface

Atlas commands should remain thin interfaces over the reasoning layer.

Commands should avoid implementing repository logic directly.

Instead, commands should request reasoning reports and render those reports in ways that support the engineer.

Example flow:

    atlas next
        ↓
    GuidanceReport
        ↓
    Repository Reasoning
        ↓
    Repository Knowledge
        ↓
    Repository

This separation allows multiple commands to reuse the same reasoning capabilities.

A command should generally render reasoning, not own reasoning.

---

## Current Implementation

The initial reasoning implementation includes:

- ImpactReport
- GuidanceReport
- analyze_impact
- build_guidance

These live in:

- tools/atlas/platform/reasoning.py

Current Atlas commands consuming the reasoning layer include:

- atlas impact
- atlas next

Future commands should extend the shared reasoning layer rather than implementing independent repository logic.

---

## Design Principles

The Repository Reasoning Layer should:

- Build upon repository knowledge rather than duplicate it.
- Reason about repository entities instead of raw Markdown files.
- Keep reasoning deterministic and explainable.
- Prefer canonical documentation over generated artifacts.
- Encourage architecture-first engineering.
- Reuse reasoning across multiple Atlas commands.
- Represent relationships once and consume them from shared reasoning capabilities.
- Treat commands as views over reasoning results.
- Guide engineers without pretending to make major architecture decisions automatically.

---

## Long-Term Direction

The long-term goal of Atlas is not to become an autonomous engineer.

Atlas should become the deterministic reasoning engine for the Aiden Platform repository.

The repository preserves engineering knowledge.

The knowledge layer understands repository structure.

The reasoning layer evaluates engineering implications.

The engineering interface exposes those capabilities through predictable commands.

This allows humans, AI assistants, and future Aiden Platform tools to work from the same repository-grounded understanding.
