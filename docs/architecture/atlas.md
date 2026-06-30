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

```text
Engineering Interface

↓

Repository Reasoning Layer

↓

Repository Knowledge Layer

↓

Repository
```

Each layer has a distinct responsibility.

The repository stores engineering knowledge.

The Repository Knowledge Layer understands repository entities.

The Repository Reasoning Layer evaluates engineering implications.

The Engineering Interface exposes deterministic capabilities through user-facing commands.

Each layer builds upon the one below it without duplicating responsibility.

---

# Repository

The repository remains the canonical source of engineering truth.

Architecture documents define engineering intent.

Infrastructure documents describe implementation.

Operations documents describe engineering workflow.

Roadmaps describe future engineering direction.

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

Current reasoning capabilities include:

- Impact analysis
- Engineering guidance
- Repository validation

Future reasoning capabilities may include:

- Repository synchronization
- Documentation consistency analysis
- Capability-aware planning
- Repository health assessment
- Change impact prediction
- Engineering recommendations

Reasoning should remain deterministic, explainable, and directly traceable to repository knowledge.

---

# Engineering Interface

The Engineering Interface exposes repository capabilities through lightweight commands.

Commands should remain presentation layers.

They should request engineering information from reusable capabilities instead of implementing engineering logic directly.

Examples include:

- atlas state
- atlas doctor
- atlas docs
- atlas explain
- atlas impact
- atlas validate
- atlas next

Future commands should begin by identifying the engineering question they answer rather than introducing new command-specific logic.

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