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
- current mission
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
2. Current mission
3. Infrastructure records
4. Operations records
5. Roadmaps
6. Generated context
7. Git state
8. Current conversation

Generated context may accelerate understanding, but it should not replace canonical documents.

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

Useful startup commands include:

    ./atlas doctor
    ./atlas validate
    ./atlas state
    ./atlas next

Future Atlas work may provide a dedicated session bootstrap command such as:

    ./atlas session

or:

    ./atlas start

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

## 5. Implement

Only begin implementation after the session has enough context to avoid assumption-driven work.

## 6. Verify

Run the appropriate verification commands for the change.

## 7. Document

Update canonical documentation, generated context, metadata, or operational records as needed.

## 8. Synchronize

Ensure the repository layers still agree after the change.

## 9. Commit and Push

Commit only after verification and documentation are complete.

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
- current branch
- validation status
- active mission
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

A session is not ready for implementation until it understands the platform well enough to avoid preventable mistakes.

Engineering sessions should improve the platform not only through planned work, but also by revealing where the platform is not yet self-explanatory.