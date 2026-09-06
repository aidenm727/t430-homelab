# Engineering Session Architecture

## Purpose

An engineering session is a focused period of work used to evolve the Aiden Platform.

Engineering sessions may involve a human engineer, an AI assistant, Atlas, or some combination of them.

The purpose of this document is to define how engineering sessions should begin, what must be understood before implementation, and how the implemented Atlas interface supports deterministic session startup.

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

The implemented startup and inspection interface reports repository metadata
validity, typed active state and mission context, relevant architecture,
generated synchronization, documentation gaps, and recommended next action.

Native execution-environment readiness still requires the human/agent
preflight below. Repository health and Atlas guidance do not establish it.

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

## Fresh Repository Baseline

Before implementation, establish a fresh local-only baseline from the repository
root:

- current date and resolved repository root;
- active branch, `HEAD`, local branch identity, and locally observed tracking
  identity;
- local ahead/behind divergence when tracking evidence exists;
- full porcelain status including staged, unstaged, and untracked paths;
- staged and unstaged name-status and `git diff --check` results;
- `./atlas bootstrap`, state, validation, missing-definition,
  synchronization, review, and next-action observations as relevant; and
- canonical active state plus its Current Mission companion.

Treat remote-tracking refs as local observations. Do not fetch, contact a host,
or mutate a ref merely to make the baseline fresh. Preserve unrelated user
changes. A missing required source, unexpected dirty path, invalid state, or
material Atlas contradiction fails closed before mutation unless the exact
condition is already inside the authorized checkpoint.

## Native Environment Preflight

Before the first mutation and before native verification, establish and record:

- exact runtime and relevant tool versions;
- a task-specific writable temporary directory;
- filesystem permissions for authorized targets, without probing unauthorized
  paths;
- exact data roots and whether each is synthetic or live;
- network and sandbox restrictions;
- required host dependencies, devices, services, mounts, and platform
  assumptions; and
- ability to start the intended focused and final broad verification commands
  through a safe smoke, discovery, import, or existing focused check.

Live or sensitive roots require exact access authority. Synthetic selected,
idle, and error fixtures must not derive behavior from mutable canonical state.
The repository root may serve as a live fixture only for an explicitly named
current-repository smoke boundary.

Classify preflight and verification failures truthfully:

- a missing runtime/tool, unwritable temporary root, denied permission,
  unavailable data root, sandbox restriction, or absent host dependency is an
  **environment failure** when product behavior has not executed in the
  accepted environment;
- a failed assertion or observable behavior after execution begins in the
  accepted environment is a **product failure**; and
- an ambiguous failure remains **unresolved** until evidence distinguishes it.

Environment remediation may continue only inside the accepted repository,
dependency, and configuration boundary. Otherwise stop for owner scope
expansion. Do not install dependencies, change configuration, probe a network,
or access credentials merely to make preflight pass.

Record the accepted native environment and checkpoint-specific verification
command in the brief. A generic preflight helper is not the default; repeated
stable evidence from at least two real checkpoints is required before proposing
automation.

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

Complete the fresh repository baseline and preserve any unrelated changes.

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

Classify the selected work under Workflow v1.1 and record its checkpoint brief.

## 5. Preflight

Establish the native execution environment, data roots, permissions,
restrictions, host assumptions, and command-start readiness before mutation.

## 6. Implement

Only begin implementation after the session has enough context to avoid
assumption-driven work and explicit owner instruction has separately established
bounded implementation authority.

## 7. Verify

Run the appropriate verification commands for the change.

## 8. Document

Update canonical documentation, generated context, metadata, or operational records as needed.

## 9. Synchronize

Ensure the repository layers still agree after the change.

## 10. Review and Accept

Complete the tier-required independent review, finding disposition, and owner
acceptance for the exact final candidate.

## 11. Publish or Deploy

Stage, commit, push, publish, or deploy only after verification, documentation,
required review, and owner acceptance are complete and the owner has separately
authorized the exact paths, refs or targets, modes, and external-write actions.

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

The current bootstrap, state, validation, synchronization, missing-definition,
review, and next-action interfaces already provide the bounded repository
inspection baseline. Generated context and the bounded task-context compilation
library also exist under their canonical owners.

Possible future improvements include interactive session assistance,
provider-specific context delivery, and broader environment or architecture
relevance assistance. These remain future capabilities, not prerequisites or
new requirements for the current startup procedure.

The long-term goal is for any future engineering session to begin from the same reliable platform understanding, regardless of whether the session is led by a human, an AI assistant, or Atlas itself.

---

# Engineering Principle

A session is not ready for deliberate engineering judgment until it understands
the platform well enough to avoid preventable mistakes. Understanding and
repository health do not establish implementation authority.

Engineering sessions should improve the platform not only through planned work, but also by revealing where the platform is not yet self-explanatory.
