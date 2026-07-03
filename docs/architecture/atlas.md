# Atlas Architecture

## Purpose

Atlas is the deterministic engineering interface for the Aiden Platform.

Its purpose is to reduce friction between engineering intent and implementation while increasing understanding of the platform.

Atlas provides a consistent engineering interface for inspecting repository state, understanding architecture, validating engineering work, preparing AI context, and guiding engineers through the engineering lifecycle.

Atlas does not replace architectural judgment.

Instead, it exposes deterministic repository knowledge and engineering reasoning so that humans and AI assistants can make better engineering decisions.

---

# Role in the Aiden Platform

The Aiden Platform consists of several complementary systems.

The repository is the canonical engineering record.

Aiden represents the long-term intelligence and assistant capabilities of the platform.

Atlas is the deterministic engineering interface that allows engineers and AI assistants to understand, inspect, validate, and evolve the repository.

Rather than becoming another engineering tool, Atlas is intended to become the primary interface through which engineering work is performed.

---

# Architectural Position

Atlas is organized as a layered engineering system.

    Repository
        ↓
    Repository Knowledge
        ↓
    Repository Reasoning
        ↓
    Engineering Intelligence
        ↓
    Engineering Interpretation
        ↓
    Engineering Interfaces

Each layer has one responsibility.

- Repository preserves canonical engineering truth.
- Repository Knowledge understands what exists.
- Repository Reasoning evaluates what is true.
- Engineering Intelligence composes reasoning into a structured engineering picture.
- Engineering Interpretation turns structured engineering intelligence into deterministic engineering guidance.
- Engineering Interfaces present that guidance through commands, assistant workflows, local tools, and future platform surfaces.

Each layer should build on the layer below it without duplicating responsibility.

---

# Layer Responsibility Model

Each Atlas layer should answer one engineering question and answer it well.

    Repository Knowledge
        What exists?

    Repository Reasoning
        What is true?

    Engineering Intelligence
        How do those truths relate?

    Engineering Interpretation
        What should the engineer do next, and why?

    Engineering Interfaces
        How should that guidance be presented?

This principle helps prevent command-specific logic, duplicated reasoning, and unclear ownership.

When a capability starts answering multiple engineering questions, it should usually be split into separate reusable capabilities or moved to the correct layer.

---

# Repository

The repository remains the canonical source of engineering truth.

Architecture documents define engineering intent.

Infrastructure documents describe implementation.

Operations documents describe engineering workflow.

Roadmaps describe future engineering direction.

Standards describe repeatable engineering behavior.

Generated context summarizes canonical sources but never replaces them.

Atlas should always prefer canonical repository knowledge over generated artifacts.

---

# Repository Knowledge Layer

The Repository Knowledge Layer provides a structured understanding of repository contents.

Rather than treating the repository as a collection of Markdown files, Atlas understands repository artifacts as engineering entities with defined roles and relationships.

Repository Knowledge currently includes:

- Repository discovery
- Document catalog
- Structured document metadata
- Documentation layers
- Canonical versus generated artifacts
- Engineering capabilities
- Document relationships
- Generated artifact ownership

Repository Knowledge describes what exists without making engineering conclusions.

Its responsibility is understanding.

---

# Repository Reasoning Layer

The Repository Reasoning Layer consumes Repository Knowledge and produces deterministic engineering conclusions.

Rather than rediscovering repository state, reasoning evaluates repository knowledge to help engineers understand engineering implications.

Repository Reasoning answers factual engineering questions such as:

- Is the repository metadata valid?
- Are canonical and generated artifacts synchronized?
- Which documents are related?
- What does a change affect?
- Which milestone criteria are satisfied?
- Which evidence is missing?

Current reasoning capabilities include:

- Impact analysis
- Engineering guidance
- Repository validation
- Repository synchronization
- Milestone completion reasoning
- Mission advancement reasoning

Future reasoning capabilities may include:

- Documentation consistency analysis
- Capability-aware planning
- Repository health assessment
- Change impact prediction
- Engineering opportunity analysis
- Repository consolidation analysis

Reasoning should remain deterministic, explainable, structured, and directly traceable to repository knowledge.

Reasoning should produce facts, evidence, criteria, confidence, and constraints.

Reasoning should avoid owning human-facing presentation when possible.

---

# Engineering Intelligence Layer

Engineering Intelligence composes reasoning outputs into one structured engineering picture.

It correlates validation, synchronization, mission state, milestone state, repository state, and relevant architecture so downstream capabilities can begin from the same understanding.

Engineering Intelligence answers questions such as:

- Is the engineering environment ready?
- Are there blockers?
- What is the active phase?
- What is the active milestone?
- What reasoning outputs agree or conflict?
- What evidence should downstream interpretation consider?

Engineering Intelligence should not become a presentation layer.

It should assemble structured facts, not decide how those facts should be shown in a CLI, chat session, dashboard, or future interface.

---

# Engineering Interpretation Layer

Engineering Interpretation consumes Engineering Intelligence and produces deterministic engineering guidance.

It turns structured engineering facts into actionable guidance while preserving traceability to the underlying evidence.

Engineering Interpretation answers:

    Given the current structured engineering picture,
    what should the engineer do next, and why?

Engineering Interpretation may produce:

- Recommended action
- Reason
- Priority
- Readiness judgment
- Next checkpoint
- Human-readable summary
- Suggested verification path
- Confidence and uncertainty explanation

Engineering Interpretation should not duplicate repository reasoning.

It should not inspect repository files directly when that information belongs in Repository Knowledge or Repository Reasoning.

It should not become an interface-specific renderer.

Multiple interfaces should be able to consume the same interpretation output.

---

# Engineering Interfaces

Engineering Interfaces expose Atlas capabilities through user-facing commands, assistant workflows, local tools, and future platform surfaces.

Interfaces should remain thin presentation layers.

They should request structured engineering information from reusable capabilities instead of implementing engineering logic directly.

Examples include:

- atlas bootstrap
- atlas review
- atlas next
- atlas state
- atlas doctor
- atlas docs
- atlas explain
- atlas impact
- atlas validate
- atlas sync
- ChatGPT engineering session startup
- Generated AI context
- Future dashboards
- Future VS Code integrations
- Future Aiden OS engineering workflows

Interfaces may format, filter, or display guidance.

They should not own repository reasoning, engineering intelligence, or engineering interpretation.

---

# Capability and Interface Separation

Atlas capabilities should be reusable across interfaces.

A command should begin by identifying the engineering question it answers, then delegate to the appropriate capability layer.

Examples:

    atlas review
        presents Engineering Interpretation output

    atlas bootstrap
        presents Engineering Interpretation plus startup readiness

    atlas sync
        presents Repository Synchronization reasoning

    atlas validate
        presents Repository Validation reasoning

This separation keeps Atlas from becoming a collection of command-specific scripts.

Atlas should become smarter by improving shared knowledge, reasoning, intelligence, and interpretation capabilities rather than by increasing command complexity.

---

# Execution Model

Atlas is currently executed as a repository-local engineering tool.

The canonical local invocation is:

    ./atlas <command>

Examples:

    ./atlas validate
    ./atlas doctor
    ./atlas docs
    ./atlas bootstrap

The repository-local launcher exists so engineers and AI assistants do not need to remember Python import paths or environment variables.

Internally, the launcher sets the repository tooling path and executes Atlas through Python.

This is the current development execution model, not necessarily the final packaging model.

Future execution models may include:

- an installable Python package
- a console entrypoint
- pipx-based installation
- workstation PATH integration

The long-term target interface is:

    atlas <command>

Until Atlas packaging is intentionally designed, repository-local execution through `./atlas` is the canonical interface.

---

# Engineering Workflow Awareness

Atlas models engineering workflow rather than repository state alone.

Engineering state includes signals such as:

- Git status
- Current mission
- Active engineering phase
- Documentation synchronization
- Generated context freshness
- Validation status
- Verification progress

Atlas should eventually help answer questions such as:

- Am I beginning new engineering work?
- Which architecture documents should be reviewed?
- Which generated artifacts are now stale?
- Has this engineering change been documented?
- Is the repository ready to commit?
- What is the next responsible engineering action?

Atlas should guide engineers through the engineering lifecycle:

```text
Design

↓

Implement

↓

Verify

↓

Document

↓

Synchronize

↓

Commit

↓

Push
```

This keeps Atlas aligned with the engineering methodology of the Aiden Platform while preserving human architectural judgment.

---

# AI-Assisted Engineering

Atlas serves as the deterministic bridge between AI assistants and the Aiden Platform repository.

Rather than relying on conversational memory, AI assistants should consult Atlas to understand current engineering state before proposing implementation work.

Atlas startup behavior and human-AI engineering session behavior are governed by:

    docs/standards/engineering-collaboration.md

Atlas should provide the deterministic live-state inputs required by that collaboration contract.

Atlas should help AI assistants determine:

- Current engineering state
- Relevant architecture
- Repository ownership
- Documentation responsibilities
- Generated artifacts requiring synchronization
- Repository validation status
- Recommended engineering workflow

The long-term objective is for Atlas to become the primary deterministic interface through which AI assistants understand the engineering platform.

---

# Internal Implementation

Atlas should remain organized around reusable engineering capabilities rather than commands.

Conceptually, Atlas consists of:

```text
commands/

↓

reasoning/

↓

knowledge/

↓

platform adapters
```

Commands present information.

Reasoning evaluates engineering implications.

Knowledge understands repository entities.

Platform adapters expose deterministic platform facts such as Git state, repository contents, mission documents, and filesystem information.

Each layer should remain independently reusable.

---

# Core Responsibilities

Atlas is responsible for:

- Repository discovery
- Repository knowledge
- Engineering reasoning
- Repository validation
- Engineering state inspection
- Documentation awareness
- AI context preparation
- Engineering workflow guidance

---

# Non-Responsibilities

Atlas should not:

- Replace architectural judgment
- Replace canonical documentation
- Store secrets
- Become a conversational assistant
- Duplicate existing platform capabilities
- Hide engineering complexity when understanding is more valuable

---

# Design Principles

Atlas should evolve according to the engineering methodology of the Aiden Platform.

Architecture should guide implementation.

Repository knowledge should precede reasoning.

Reasoning should precede user interfaces.

Capabilities should be reusable across commands.

Implementation should strengthen architecture rather than accumulate command-specific behavior.

Atlas should become smarter by improving its understanding of the repository rather than by increasing command complexity.

---

# Long-Term Direction

Atlas is intended to become the deterministic engineering interface for the Aiden Platform.

Its long-term purpose is not autonomous engineering.

Its purpose is to expose deterministic engineering knowledge and reasoning that improves both human and AI-assisted engineering.

As the repository evolves, Atlas should evolve by strengthening its Repository Knowledge Layer and Repository Reasoning Layer while keeping engineering interfaces thin, predictable, and reusable.