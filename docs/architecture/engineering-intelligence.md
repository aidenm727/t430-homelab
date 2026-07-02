# Engineering Intelligence Architecture

## Purpose

Engineering Intelligence is the shared platform capability that assembles repository knowledge, reasoning outputs, engineering state, and capability evidence into one structured understanding of the Aiden Platform engineering system.

Its purpose is to help humans, Atlas, AI assistants, local agents, and future interfaces begin from the same engineering picture.

## Core Principle

Engineering intelligence should be platform-owned, not interface-owned.

Atlas CLI, ChatGPT, local AI, VS Code, and future Aiden OS workflows should consume the same underlying engineering intelligence rather than each rebuilding their own understanding.

## Architectural Position

Engineering Intelligence sits above individual reasoning capabilities and below engineering interfaces.

    Repository
        ↓
    Repository Knowledge
        ↓
    Repository Reasoning
        ↓
    Engineering Capabilities
        ↓
    Engineering Intelligence
        ↓
    Interfaces

## Inputs

Engineering Intelligence may consume:

- Repository Validation
- Repository Synchronization
- Engineering State
- Engineering Guidance
- Milestone Completion Reasoning
- Capability Maturity
- Repository Metadata
- Current Mission
- Git State
- Generated Context Freshness

## Responsibilities

Engineering Intelligence should assemble a structured picture of:

- Repository health
- Synchronization status
- Working tree readiness
- Current mission
- Current milestone
- Capability maturity
- Completed or stale milestones
- Relevant architecture
- Recommended next engineering investment
- Evidence supporting recommendations

## Relationship to Engineering Review

Engineering Review should consume Engineering Intelligence.

Engineering Review should not become the place where all engineering reasoning is manually glued together.

Instead:

    Engineering Intelligence produces the structured picture.
    Engineering Review renders and interprets that picture.
    Interfaces display it for humans or AI systems.

## Interface Consumers

Engineering Intelligence should eventually support:

- atlas review
- atlas next
- engineering session startup
- generated AI context
- ChatGPT project workflows
- local AI agents
- VS Code integrations
- future Aiden OS workflows

## Design Rules

Engineering Intelligence must:

- Reuse existing reasoning capabilities
- Avoid duplicating validation or synchronization logic
- Produce structured evidence before rendered output
- Keep interfaces thin
- Preserve human architectural judgment
- Support multiple future interfaces
- Remain deterministic where practical

## Non-Responsibilities

Engineering Intelligence should not:

- Replace human decisions
- Automatically rewrite repository documents
- Store conversational memory
- Depend on one AI provider
- Hide uncertainty
- Duplicate canonical documentation

## Future Capability Producers

Future producers may include:

- Platform Consolidation Review
- Idea Intake and Brainstorm Review
- Software Delivery Workflows
- Context Selection Reasoning
- Repository Evolution Reasoning
- Documentation Cleanup Review
- Capability Maturity Analysis

These should plug into Engineering Intelligence rather than becoming isolated systems.

## Future Direction

Engineering Intelligence should become the normal source of truth for engineering session startup.

A future engineering session should begin from a structured intelligence report that answers:

    Is the repository healthy?
    Is the platform synchronized?
    What changed?
    What milestone appears complete?
    What capability should improve next?
    What context should an AI interface receive?

This moves the Aiden Platform toward an engineering system that can help improve itself deliberately while keeping the human engineer in control.
