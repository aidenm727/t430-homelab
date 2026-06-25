# Documentation Map

## Purpose

This document explains how the Aiden Platform documentation is organized.

It is the recommended starting point for understanding the repository.

## Documentation Layers

The documentation is organized into four layers:

```text
Vision
Architecture
Infrastructure
Operations
```

## 1. Vision

Vision documents explain why the platform exists and where it is going.

Primary documents:

* `docs/architecture/platform.md`

Future documents:

* `docs/vision.md`

## 2. Architecture

Architecture documents explain how the platform should be designed.

Primary documents:

* `docs/architecture/platform.md`
* `docs/architecture/engineering.md`
* `docs/architecture/capabilities.md`

These documents should describe principles, relationships, capabilities, and decision-making rules.

They should not become service inventories.

## 3. Infrastructure

Infrastructure documents explain what currently exists.

Primary documents:

* `docs/infrastructure.md`
* `docs/infrastructure-gamer-pve.md`
* `docs/services.md`

These documents should describe hosts, services, networking, storage, access, backups, and operational state.

## 4. Operations

Operations documents explain how changes are made, tracked, and verified.

Primary documents:

* `docs/changes.log`
* `docs/changes/*.yml`
* `docs/change-schema.md`
* `docs/change-session.md`

Operational changes should follow this workflow:

```text
Deploy / Configure
Verify
Document
Commit
Push
```

## AI Context Files

AI-facing context files summarize the project for ChatGPT or future AI assistants.

Primary documents:

* `docs/current-mission.md`
* `docs/aiden-context.md`
* `docs/infrastructure-snapshot.md`
* `docs/aiden-context-spec.md`

These files are generated or maintained to help AI assistants quickly understand the project state.

They should summarize the canonical documentation, not replace it.

## Recommended Reading Path

A new human or AI reader should read the repository in this order:

1. `README.md`
2. `docs/docs-map.md`
3. `docs/architecture/platform.md`
4. `docs/architecture/engineering.md`
5. `docs/architecture/capabilities.md`
6. `docs/current-mission.md`
7. `docs/infrastructure.md`
8. `docs/infrastructure-gamer-pve.md`
9. `docs/services.md`
10. `docs/aiden-context.md`

## Source of Truth Rules

GitHub is the canonical documentation source.

The server-side `~/homelab/docs/changes.log` is the operational history record.

Infrastructure records describe current state.

Architecture records describe intent, design, and decision-making principles.

AI context files summarize the current state for assistant workflows.

## When to Update Documents

Update architecture documents when:

* A design principle changes
* A new platform capability is defined
* The long-term direction changes
* A major decision needs explanation

Update infrastructure documents when:

* A host changes
* A service is added, removed, or reconfigured
* Networking, storage, access, or backup behavior changes
* A documented operational state becomes outdated

Update operations documents when:

* A meaningful infrastructure change is made
* A change session is started or completed
* A new change type or schema rule is introduced

Update AI context files when:

* The current mission changes
* Infrastructure documentation changes significantly
* The assistant needs newer context

## Documentation Principle

The repository should teach the platform from the top down:

```text
Why it exists
How it is designed
What currently exists
How it is operated
What is changing next
```
