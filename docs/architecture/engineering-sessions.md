# Engineering Session Architecture

## Purpose

An engineering session is a focused period of work used to evolve the Aiden Platform.

Engineering sessions may involve a human engineer, an AI assistant, Atlas, or some combination of them.

The purpose of this document is to define how engineering sessions should begin, what must be understood before implementation, and how Atlas should eventually support deterministic session startup.

A new session should not depend on memory, assumptions, or conversational context alone.

It should begin from the repository.

---

# Core Principle

Every engineering session should start from a shared, deterministic understanding of the platform.

Before implementation begins, the session should establish:

- current repository state
- canonical active state and its Current Mission companion
- relevant architecture
- Atlas validation status
- engineering environment readiness
- documentation synchronization needs
- next responsible engineering action

This protects the platform from assumption-driven work.

---

# Relationship to the Repository

The repository is the canonical source of truth for engineering sessions.

A session should prefer repository knowledge in this order:

1. Architecture
2. Canonical active state
3. Current Mission companion
4. Infrastructure records
5. Operations records
6. Roadmaps
7. Generated context
8. Git state
9. Current conversation

Generated context may accelerate understanding, but it should not replace canonical documents.

This knowledge order determines what sources to trust, not what actions are
authorized. `AGENTS.md` is the primary repository-local authority-interpretation
contract, and explicit current owner instruction remains external to repository
state.

---

# Relationship to Atlas

Atlas is the deterministic engineering interface for beginning and guiding engineering sessions.

Atlas should eventually answer:

- Is the local engineering environment ready?
- Is repository metadata valid?
- What is the active mission?
- Which architecture documents are relevant?
- Are generated artifacts synchronized?
- Are there known documentation gaps?
- What is the next responsible action?

The current repository-local Atlas invocation is:

    ./atlas <command>

The current canonical startup command is:

    ./atlas bootstrap

This command establishes deterministic repository observations and the shared
readiness projection. It does not establish task, implementation, publication,
deployment, or external-write authority.

Supporting startup commands include:

    ./atlas review
    ./atlas next
    ./atlas validate
    ./atlas sync

Future Atlas work may expand bootstrap behavior with a dedicated interactive session command such as:

    ./atlas session

Such commands should remain thin interfaces over reusable repository knowledge and reasoning capabilities.

---

# Session Startup Flow

A normal engineering session should begin with the following flow:

## 1. Inspect

Determine the current repository and engineering state.

Examples:

- Git status
- current mission
- active change session
- recent changes
- available Atlas commands

## 2. Validate

Confirm the repository is structurally usable before making changes.

Examples:

- Atlas validation
- metadata completeness
- generated artifact ownership
- required architecture documents

## 3. Orient

Identify the current engineering phase and relevant architecture.

Examples:

- platform architecture
- Atlas architecture
- repository architecture
- current roadmap
- current mission

## 4. Decide

Choose the next responsible engineering checkpoint.

This decision should be based on architecture, current mission, validation state, and observed engineering friction.

Repository work selection records the decision but does not grant permission to
act. A checkpoint may be selected only by explicit owner decision.

## 5. Implement

Only begin implementation after the session has enough context to avoid
assumption-driven work and explicit owner instruction has separately established
bounded implementation authority.

## 6. Verify

Run the appropriate verification commands for the change.

## 7. Document

Update canonical documentation, generated context, metadata, or operational records as needed.

## 8. Synchronize

Ensure the repository layers still agree after the change.

## 9. Commit and Push

Commit and push only after verification and documentation are complete and the
owner has separately authorized the exact ref and external-write actions.

---

# Session Knowledge Types

Engineering sessions rely on several kinds of knowledge.

## Architectural Knowledge

Long-term design intent.

Examples:

- platform architecture
- Atlas architecture
- repository architecture
- engineering methodology

## Operational Knowledge

Knowledge discovered by using and operating the platform.

Examples:

- Atlas invocation requirements
- common setup failures
- missing entrypoints
- recurring validation failures
- friction observed during real sessions

## Repository Knowledge

Structured knowledge about repository entities.

Examples:

- document metadata
- canonical versus generated files
- document relationships
- capability ownership

## Engineering State

Current local and repository state.

Examples:

- Git status
- current branch as a live observation
- validation status
- canonical phase and selected work
- task, implementation, and publication authority as external/not established by Atlas
- staged changes
- untracked files

---

# Lessons from Fresh Sessions

Fresh sessions are valuable because they reveal what the repository does not yet explain well enough.

If a human or AI assistant makes incorrect assumptions during session startup, the response should not only be to fix the immediate issue.

The session should also identify what repository, Atlas, or documentation improvement would have prevented the assumption.

Platform use is a form of verification.

---

# Non-Responsibilities

Engineering Session Architecture should not:

- replace the engineering methodology
- duplicate the Atlas roadmap
- become a change log
- store temporary notes
- replace canonical architecture
- define every Atlas command in detail

Its responsibility is to define how engineering work should begin and how session startup should become deterministic.

---

# Future Direction

Future Atlas capabilities should make session startup increasingly automatic.

Possible future improvements include:

- session bootstrap command
- engineering readiness report
- synchronization report
- fresh-session checklist
- AI context preparation
- architecture relevance detection
- current mission summary
- next-action recommendation

The long-term goal is for any future engineering session to begin from the same reliable platform understanding, regardless of whether the session is led by a human, an AI assistant, or Atlas itself.

---

# Engineering Principle

A session is not ready for deliberate engineering judgment until it understands
the platform well enough to avoid preventable mistakes. Understanding and
repository health do not establish implementation authority.

Engineering sessions should improve the platform not only through planned work, but also by revealing where the platform is not yet self-explanatory.
