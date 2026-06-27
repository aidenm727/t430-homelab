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