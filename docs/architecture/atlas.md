# Atlas Architecture

## Purpose

Atlas is the engineering toolkit for the Aiden Platform.

It exists to reduce friction between an idea and a well-engineered implementation while increasing understanding of the platform.

Atlas should become the primary command-line interface for inspecting, validating, documenting, and preparing engineering work on the Aiden Platform.

## Role in the Platform

The Aiden Platform is the overall personal infrastructure system.

Aiden is the future intelligence and assistant layer.

Atlas is the deterministic engineering toolkit.

Atlas does not replace architectural judgment. It supports engineering judgment by exposing state, checking consistency, preparing context, and automating repeatable workflows.

## Engineering Workflow Awareness

Atlas should model engineering workflow, not only repository state.

Git status, documentation state, active change sessions, generated context, and verification results are signals that help Atlas understand where engineering work currently stands.

Atlas should eventually help answer:

- Am I starting new work?
- Am I in the middle of an active change?
- Has the change been verified?
- Has documentation been updated?
- Is AI context stale?
- Is the repository ready to commit?
- What is the next responsible engineering action?

Atlas should not merely report that the working tree is dirty. It should help interpret whether that state is expected, incomplete, risky, or ready to finalize.

The long-term goal is for Atlas to guide the platform through the engineering lifecycle:

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

This keeps Atlas aligned with the Aiden Platform methodology while preserving human architectural judgment.

## Engineering Questions

Atlas exists to answer deterministic engineering questions.

Every Atlas capability should answer one engineering question.

Examples include:

- Where am I?
  - `atlas state`
- Is my engineering environment healthy?
  - `atlas doctor`
- What changed?
  - `atlas change`
- Is documentation synchronized?
  - `atlas docs`
- What should I do next?
  - `atlas next`
- Prepare engineering context.
  - `atlas context`

Future capabilities should begin by identifying the engineering question being answered rather than proposing a command directly.

## Repository Knowledge Model

Atlas should maintain an internal understanding of repository knowledge rather than treating the repository as a collection of files.

### Repository Discovery

Repository discovery identifies engineering artifacts and classifies them into documentation layers such as Architecture, Infrastructure, Operations, Roadmaps, Current Context, and future categories.

Discovery answers:

- What exists?
- Where is it located?
- Which layer does it belong to?

### Document Catalog

The Document Catalog builds on repository discovery by describing each document as an engineering artifact.

Each document should expose metadata such as:

- Name
- Documentation layer
- Purpose
- Canonical status
- Generated status
- Primary engineering capability
- Related documents
- Validation rules (future)

The Document Catalog should become the primary source of repository knowledge for Atlas.

Commands should consume the Document Catalog rather than independently traversing the repository.

### Design Principles

The repository should not contain engineering knowledge that Atlas cannot discover, classify, or explain.

Repository understanding should be capability-driven rather than command-driven.

As the repository evolves, Atlas should evolve by improving its repository knowledge model instead of accumulating command-specific logic.

## AI-Assisted Engineering Interface

Atlas should serve as the deterministic bridge between AI assistants and the Aiden Platform repository.

AI assistants should use Atlas to inspect current engineering state, discover repository artifacts, explain documents, navigate canonical sources, and identify missing repository knowledge before proposing implementation work.

This keeps AI-assisted engineering grounded in repository state rather than chat memory alone.

Atlas should eventually help AI assistants answer:

- What is the current engineering state?
- Which documents are relevant to this task?
- Which artifact owns this capability?
- What documentation may need synchronization after a change?
- Which generated context may be stale?
- What should be verified before committing?

The long-term goal is for AI assistants to use Atlas as the primary deterministic interface for planning, editing, validating, documenting, and synchronizing Aiden Platform engineering work.

## Internal Architecture

Atlas should be organized as a layered engineering system.

### Presentation Layer

The presentation layer contains user-facing commands such as:

- atlas state
- atlas doctor
- atlas next
- atlas docs

Commands should remain thin. They should present engineering information rather than independently rediscovering repository state.

### Capability Layer

The capability layer contains reusable engineering concepts such as:

- EngineeringState
- Discovery
- RepositoryHealth (future)
- DocumentManagement (future)
- ChangeHistory (future)

Capabilities should answer deterministic engineering questions and be reused by multiple commands where appropriate.

### Platform Adapter Layer

The platform adapter layer contains low-level readers for Git, mission files, repository paths, filesystem state, and future operational signals.

Adapters expose platform facts.

Capabilities interpret those facts.

Commands present the results.

## Core Responsibilities

Atlas may provide capabilities such as:

- Engineering state inspection
- Context generation and preparation
- Change workflow assistance
- Documentation validation
- Repository validation
- Architecture awareness
- Operational readiness checks
- Future unified engineering CLI

## Non-Responsibilities

Atlas should not:

- Make major architecture decisions automatically
- Replace canonical documentation
- Store secrets
- Become a general chatbot
- Duplicate existing tools without clear reason
- Hide infrastructure complexity when understanding is needed

## Design Principles

Atlas should follow the Aiden Platform engineering methodology:

1. Learn
2. Design
3. Implement
4. Verify
5. Document
6. Commit

Before implementing a new Atlas feature, first determine whether the capability already exists elsewhere in the platform.

If the capability exists, Atlas should integrate with it rather than duplicate it.

If the capability does not exist, Atlas should add the smallest useful improvement that can be verified.

## Initial Capability Model

### Engineering State

Atlas should answer:

- What is the current mission?
- What infrastructure exists?
- What changed recently?
- Is there an active change session?
- What is the next milestone?

### Context Management

Atlas should help prepare AI-readable context from canonical documentation.

Generated context should summarize authoritative sources, not replace them.

### Change Management

Atlas should support the structured change workflow.

It should help make changes easier to start, verify, document, commit, and push.

### Documentation Assistance

Atlas should help identify documentation gaps, outdated records, and missing updates.

### Repository Validation

Atlas should help verify that the repository is organized, consistent, and ready for engineering work.

## First Implementation Target

The first Atlas command should be:

python tools/atlas.py state