# Engineering Capabilities Architecture

## Purpose

Engineering capabilities are reusable platform abilities that help the Aiden Platform understand, inspect, validate, synchronize, and evolve itself.

They sit between repository reasoning and user-facing interfaces.

Atlas is the first interface exposing these capabilities, but the capabilities should not belong only to the Atlas CLI.

## Core Principle

Capabilities are reusable.

Interfaces are replaceable.

A capability should answer an engineering question or perform an engineering function in a way that can be reused by multiple interfaces.

## Architectural Position

The engineering stack should evolve toward this model:

    Repository
        ↓
    Repository Knowledge
        ↓
    Repository Reasoning
        ↓
    Engineering Capabilities
        ↓
    Interfaces

Interfaces may include:

- Atlas CLI
- ChatGPT project workflows
- Local AI assistants
- VS Code integrations
- Automation workflows
- Future web or desktop interfaces

## Capability Definition

An engineering capability is a reusable function of the platform that helps perform engineering work.

A capability should:

- Improve understanding
- Reduce engineering friction
- Use repository knowledge
- Reuse repository reasoning where appropriate
- Remain deterministic where practical
- Be exposed through one or more interfaces
- Avoid duplicating logic across commands

## Capability vs Command

Commands are interfaces.

Capabilities are reusable engineering functions.

A command should render or invoke a capability.

A command should not become the only place where engineering logic exists.

For example:

    atlas impact

is an interface to the Impact Analysis capability.

The Impact Analysis capability should remain reusable by future interfaces beyond the CLI.

## Capability vs Repository Knowledge

Repository Knowledge answers:

- What exists?
- What layer does it belong to?
- What does it mean?
- What is it related to?
- Is it canonical or generated?
- Which capability does it support?

Engineering capabilities use that knowledge to support engineering work.

Knowledge describes repository facts.

Capabilities apply repository facts to engineering workflows.

## Capability vs Repository Reasoning

Repository Reasoning produces deterministic conclusions from repository knowledge.

Engineering capabilities may compose one or more reasoning functions into useful workflows.

For example:

- Impact Analysis uses relationship reasoning.
- Engineering Guidance uses mission, git state, and repository knowledge.
- Repository Validation uses catalog and metadata consistency checks.
- Future Repository Synchronization may use git state, generated artifact ownership, and document relationships.

Reasoning should remain reusable beneath capabilities.

Capabilities should organize reasoning into practical engineering functions.

## Current Capabilities

### Repository Documentation Discovery

Current interface:

- atlas docs

Purpose:

Show repository documents grouped by documentation layer.

Current maturity:

Operational.

### Document Explanation

Current interface:

- atlas explain

Purpose:

Explain what Atlas knows about a repository document.

Current maturity:

Operational.

### Repository Validation

Current interface:

- atlas validate

Purpose:

Check whether discovered repository documents and metadata definitions are internally consistent.

Current maturity:

Operational and growing.

### Impact Analysis

Current interface:

- atlas impact

Purpose:

Identify related documents, generated outputs, and likely follow-up actions for a repository artifact.

Current maturity:

Operational and growing.

### Engineering Guidance

Current interface:

- atlas next

Purpose:

Recommend the next engineering action based on mission, repository state, and repository reasoning.

Current maturity:

Early but useful.

### Engineering State Inspection

Current interface:

- atlas state

Purpose:

Show the current engineering state, including mission, git status, and repository sources.

Current maturity:

Operational but should evolve as repository knowledge grows.

### Engineering Environment Health

Current interface:

- atlas doctor

Purpose:

Check whether the local engineering environment is ready for platform work.

Current maturity:

Basic.

## Future Capabilities

Future engineering capabilities may include:

- Repository Synchronization
- Generated Context Freshness
- Standards Awareness
- Capability-Aware Planning
- Documentation Consistency Review
- Engineering Session Bootstrap
- Commit Readiness Review
- Repository Metadata Migration Support

Each future capability should be designed as reusable platform logic before being exposed through commands.

## Design Rules

When adding a new engineering capability:

1. Identify the engineering question it answers.
2. Determine which repository knowledge it needs.
3. Determine which reasoning functions it should reuse.
4. Define the capability independently from any single command.
5. Expose the capability through the smallest useful interface.
6. Verify the capability directly before expanding interface behavior.

## Interface Rules

Interfaces should remain thin.

Interfaces should:

- Parse user intent
- Request capability output
- Render results clearly
- Avoid duplicating repository logic
- Avoid owning reasoning that belongs in reusable modules

If two commands need the same logic, that logic belongs in a shared capability or reasoning layer.

## Relationship to Atlas

Atlas is the first deterministic engineering interface for the Aiden Platform.

Atlas should expose engineering capabilities without owning all capability logic inside command modules.

Over time, Atlas should become one interface over a broader engineering engine.

The long-term goal is for engineering capabilities to support:

- human engineers
- AI assistants
- local automation
- future Aiden OS workflows

## Non-Responsibilities

Engineering capabilities should not:

- Replace architectural judgment
- Hide repository complexity when understanding is important
- Duplicate canonical documentation
- Store secrets
- Become conversational memory
- Depend on a single AI provider or interface

## Implementation Direction

The current Atlas implementation already contains early engineering capabilities.

The next implementation work should strengthen existing capabilities before adding many new commands.

Near-term priorities:

1. Keep commands thin.
2. Strengthen the repository knowledge model.
3. Make engineering state aware of all repository layers.
4. Keep reasoning reusable.
5. Introduce new commands only when they expose a clear capability.

This keeps Atlas aligned with the Aiden Platform principle that capabilities matter more than tools.
