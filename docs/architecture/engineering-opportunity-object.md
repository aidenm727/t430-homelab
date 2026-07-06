# Engineering Opportunity Object Architecture

## Purpose

An Engineering Opportunity Object is the repository-native record of a potential engineering improvement for the Aiden Platform.

Its purpose is to preserve useful engineering possibilities before they become active engineering work.

Engineering Opportunity Objects prevent valuable ideas from being lost in conversation, scattered notes, or temporary engineering sessions.

They transform future engineering possibilities into durable repository knowledge.

---

## Core Principle

Engineering opportunities are first-class repository objects.

They should be explicit, structured, reviewable, searchable, and lifecycle-aware.

An opportunity is not automatically a task.

An opportunity is a preserved engineering possibility that may later become architecture, roadmap work, mission work, implementation, or be intentionally discarded.

---

## Architectural Position

Engineering Opportunity Objects belong to the Engineering capability of the Aiden Platform.

They support Engineering Opportunity and Engineering Opportunity Intelligence.

    Engineering Opportunity
        ↓
    Engineering Opportunity Object
        ↓
    Engineering Opportunity Intelligence
        ↓
    Engineering Interpretation
        ↓
    Engineering Review
        ↓
    Engineering Interfaces

Engineering Opportunity defines the lifecycle.

Engineering Opportunity Objects preserve individual opportunities.

Engineering Opportunity Intelligence evaluates them.

Atlas exposes and reasons about them.

---

## Repository Ownership

Engineering Opportunity Objects are owned by the repository.

The canonical location is:

    docs/opportunities/captured/

Future lifecycle-specific directories may include:

    docs/opportunities/reviewed/
    docs/opportunities/accepted/
    docs/opportunities/architected/
    docs/opportunities/scheduled/
    docs/opportunities/implemented/
    docs/opportunities/closed/

The repository remains the canonical source of truth for opportunity state.

Conversation may identify opportunities.

The repository owns them.

---

## Object Format

Engineering Opportunity Objects should be stored as small structured files.

The initial storage format is YAML.

YAML is appropriate because opportunity objects are:

- structured
- human readable
- easy to diff
- deterministic for Atlas
- suitable for future schema evolution

Future formats may be introduced only if they improve repository reasoning without reducing human readability.

---

## Required Fields

Every Engineering Opportunity Object should contain:

- id
- title
- status
- capability
- created
- source
- summary
- rationale

These provide enough information for discovery, review, and reasoning.

---

## Optional Fields

Engineering Opportunity Objects may also contain:

- priority
- effort
- impact
- dependencies
- related_documents
- related_opportunities
- evidence
- notes
- decision
- closed_reason
- implemented_by
- completed

Optional fields should be introduced only when they improve engineering reasoning.

---

## Identifier Rules

Each opportunity should have a stable identifier.

Initial identifier format:

    EO-YYYY-NNN

Example:

    EO-2026-001

The identifier should never change throughout the object's lifecycle.

Stable identifiers allow opportunities to be referenced by architecture, missions, roadmaps, commits, and Atlas output.

---

## Lifecycle

Engineering Opportunity Objects progress through the following lifecycle.

    captured
        ↓
    reviewed
        ↓
    accepted
        ↓
    architected
        ↓
    scheduled
        ↓
    implemented
        ↓
    closed

Not every opportunity must pass through every state.

Some may be closed after review.

Some may remain captured for long periods.

Some may become architecture before they become scheduled implementation work.

---

## Lifecycle State Definitions

### Captured

The opportunity has been preserved.

It has not yet been evaluated.

### Reviewed

The opportunity has been examined for duplication, architectural fit, and engineering value.

### Accepted

The opportunity is considered worthwhile future work.

Acceptance does not imply scheduling.

### Architected

The opportunity has enough design guidance to support implementation.

### Scheduled

The opportunity has been selected for active engineering work.

### Implemented

The engineering change has been completed and verified.

### Closed

The opportunity has been completed, rejected, merged, superseded, or intentionally retired.

---

## Status Rules

The status field represents the current lifecycle state.

Status should change only when there is a clear engineering reason.

Atlas should eventually validate that repository location and object status agree.

For example:

    docs/opportunities/captured/

should normally contain:

    status: captured

---

## Relationship to Architecture

Engineering Opportunity Objects are not architecture documents.

They may identify missing architecture.

They may eventually produce architecture.

They do not replace architectural design.

If durable design decisions are required, they belong in architecture documentation.

---

## Relationship to Roadmaps

Roadmaps describe planned direction.

Engineering Opportunity Objects describe individual engineering possibilities.

A roadmap may reference many opportunities.

An opportunity may influence multiple future roadmaps.

---

## Relationship to Missions

Mission documents describe current engineering focus.

Engineering Opportunity Objects describe possible future engineering work.

Engineering Opportunity Intelligence may eventually recommend promoting an opportunity into a future mission.

---

## Relationship to Atlas

Atlas should understand Engineering Opportunity Objects as repository entities.

Atlas should eventually be able to:

- discover opportunities
- validate opportunity schemas
- detect duplicates
- summarize opportunity state
- relate opportunities to architecture
- relate opportunities to missions
- recommend lifecycle progression
- expose opportunity intelligence through Engineering Review

Commands should remain thin interfaces over reusable reasoning capabilities.

---

## Relationship to Engineering Opportunity Intelligence

Engineering Opportunity Intelligence evaluates Engineering Opportunity Objects.

It determines:

- whether an opportunity is valid
- whether it duplicates existing work
- whether it improves a platform capability
- whether sufficient evidence exists
- whether architecture is required
- whether implementation should be recommended
- whether the opportunity should remain deferred

The object stores the opportunity.

Engineering Opportunity Intelligence reasons about it.

---

## Example Object

    id: EO-2026-001
    title: Reliable implementation artifact transport
    status: captured
    capability: Engineering
    created: 2026-07-06
    source: engineering-session
    summary: >
      Large implementation artifacts occasionally become corrupted during
      ChatGPT response rendering, breaking copy-paste engineering workflows.
    rationale: >
      Repeated engineering sessions have exposed transport reliability
      issues with large Markdown artifacts.
    notes: >
      Candidate future improvements include transport selection,
      repository-native patch application, and future Atlas apply workflows.

---

## Design Rules

Engineering Opportunity Objects must:

- preserve engineering opportunities
- remain understandable to humans
- remain deterministic for Atlas
- avoid replacing architecture
- avoid becoming free-form notes
- avoid duplicating operational change records
- support evidence-backed reasoning
- support lifecycle progression

---

## Non-Responsibilities

Engineering Opportunity Objects should not:

- replace architecture
- replace roadmaps
- replace missions
- replace operational history
- authorize implementation
- store secrets
- become conversational transcripts

---

## Completion Criteria

This architecture is considered established when:

- the object purpose is documented
- the lifecycle is documented
- required fields are defined
- repository ownership is defined
- Atlas recognizes the object architecture
- at least one captured object exists
- Engineering Opportunity Intelligence can reason about these objects

---

## Future Direction

Engineering Opportunity Objects should become a foundational repository entity for Atlas Engineering Intelligence.

As Atlas evolves, it should reason across Engineering Opportunity Objects, architecture, missions, repository state, synchronization, validation, and engineering history to continuously identify high-leverage engineering improvements while preserving deliberate human judgment.
