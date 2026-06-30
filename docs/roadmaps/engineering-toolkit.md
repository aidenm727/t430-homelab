# Aiden Engineering Toolkit Roadmap

## Purpose

The Aiden Engineering Toolkit is the engineering software layer of the Aiden Platform.

Its purpose is to reduce engineering friction, expose deterministic repository knowledge, guide engineering workflow, and provide a consistent interface for both humans and AI assistants.

The long-term objective is to make engineering work increasingly capability-driven rather than tool-driven.

---

# Vision

Atlas is evolving into the deterministic engineering interface for the Aiden Platform.

Rather than becoming a collection of independent utilities, Atlas should become a layered engineering platform that understands repository knowledge, performs deterministic reasoning, and exposes reusable engineering capabilities through a unified interface.

Engineering capabilities should evolve before engineering commands.

Commands should remain lightweight interfaces over reusable platform capabilities.

---

# Current Toolkit

The engineering toolkit currently includes:

## Atlas

Deterministic engineering interface for repository inspection, reasoning, validation, and workflow guidance.

## generate-context.py

Generates AI-readable engineering context from canonical documentation.

## homelab-change.py

Supports structured engineering change sessions, change history, and documentation synchronization.

## aiden-context-loader.py

Prototype engineering-state summary utility.

---

# Current Architecture

Atlas currently consists of four conceptual layers.

```text
Engineering Interface

↓

Repository Reasoning Layer

↓

Repository Knowledge Layer

↓

Repository
```

Current engineering work expands these layers rather than introducing command-specific behavior.

---

# Completed Capabilities

## Repository Knowledge

Completed:

- Repository discovery
- Documentation layer classification
- Document Catalog
- Structured document metadata
- Repository navigation
- Canonical versus generated document awareness
- Engineering capability metadata

---

## Repository Reasoning

Completed:

- Repository impact analysis
- Engineering guidance
- Repository validation

These capabilities provide deterministic engineering reasoning built on Repository Knowledge.

---

## Engineering Interface

Implemented commands:

```text
atlas state
atlas doctor
atlas docs
atlas explain
atlas impact
atlas validate
atlas missing
atlas open
atlas next
```

Commands remain presentation layers over reusable engineering capabilities.

---

# Current Engineering Milestone

The active engineering milestone is:

## Repository Synchronization Reasoning

Goals include:

- Detect documentation requiring synchronization
- Detect stale generated artifacts
- Detect architecture and implementation drift
- Detect roadmap synchronization opportunities
- Recommend engineering synchronization actions

---

# Upcoming Capabilities

Following Synchronization Reasoning, planned capability work includes:

## Repository Reasoning

- Planning Reasoning
- Documentation consistency analysis
- Repository health assessment
- Engineering recommendation engine
- Capability-aware planning
- Change impact prediction

## Repository Knowledge

- Relationship-aware repository model
- Repository relationship graph
- Capability graph
- Dependency graph
- Rich repository metadata

## Engineering Interface

Future interface capabilities may include:

- Repository search
- Engineering inbox
- Context preparation
- Roadmap inspection
- Architecture navigation
- Repository synchronization
- Workflow automation

These interfaces should remain thin wrappers over reusable engineering capabilities.

---

# Engineering Principles

Atlas should continue evolving according to the engineering methodology of the Aiden Platform.

Development should follow:

```text
Architecture

↓

Capability

↓

Implementation

↓

Verification

↓

Documentation

↓

Synchronization

↓

Commit
```

Capabilities should always precede interfaces.

Architecture should guide implementation.

Repository knowledge should strengthen reasoning.

Reasoning should strengthen engineering interfaces.

---

# Long-Term Direction

The long-term objective is for Atlas to become the deterministic engineering interface for the entire Aiden Platform.

As the platform evolves, Atlas should improve by:

- Strengthening Repository Knowledge
- Expanding Repository Reasoning
- Keeping engineering interfaces lightweight
- Increasing deterministic understanding of repository state
- Improving AI-assisted engineering without replacing architectural judgment

Every engineering improvement should make Atlas better at understanding the repository rather than simply increasing the number of available commands.