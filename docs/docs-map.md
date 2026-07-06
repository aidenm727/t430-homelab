# Documentation Map

## Purpose

This document explains how the Aiden Platform documentation is organized.

It is the recommended starting point for understanding the repository.

## Documentation Layers

The documentation is organized into five layers:

    Vision
    Architecture
    Standards
    Infrastructure
    Operations

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
* `docs/architecture/engineering-capabilities.md`
* `docs/architecture/engineering-review.md`
* `docs/architecture/engineering-intelligence.md`
* `docs/architecture/engineering-opportunity.md`
* `docs/architecture/milestone-completion.md`
* `docs/architecture/mission-advancement.md`
* `docs/architecture/engineering-lifecycle.md`
* `docs/architecture/architecture-registration.md`
* `docs/architecture/capabilities.md`
* `docs/architecture/repository-metadata.md`

These documents should describe principles, relationships, capabilities, and decision-making rules.

They should not become service inventories.

## 3. Standards

Standards documents explain how engineering work should be performed.

Primary documents:

* `docs/standards/engineering-collaboration.md`

These documents should define repeatable expectations, workflows, formatting rules, and quality bars for building the platform.

They should not replace architecture, infrastructure records, or operational history.

## 4. Infrastructure

Infrastructure documents explain what currently exists.

Primary documents:

* `docs/infrastructure.md`
* `docs/infrastructure-gamer-pve.md`
* `docs/services.md`

These documents should describe hosts, services, networking, storage, access, backups, and operational state.

## 5. Operations

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
5. `docs/architecture/engineering-capabilities.md`
6. `docs/architecture/engineering-review.md`
7. `docs/architecture/engineering-intelligence.md`
8. `docs/architecture/engineering-opportunity.md`
9. `docs/architecture/milestone-completion.md`
10. `docs/architecture/mission-advancement.md`
11. `docs/architecture/engineering-lifecycle.md`
12. `docs/architecture/architecture-registration.md`
13. `docs/architecture/capabilities.md`
14. `docs/architecture/compute.md`
15. `docs/architecture/ai.md`
16. `docs/architecture/repository.md`
17. `docs/architecture/atlas.md`
18. `docs/architecture/repository-metadata.md`
19. `docs/standards/engineering-collaboration.md`
20. `docs/current-mission.md`
21. `docs/infrastructure.md`
22. `docs/infrastructure-gamer-pve.md`
23. `docs/services.md`
24. `docs/aiden-context.md`

## Source of Truth Rules

GitHub is the canonical documentation source.

The server-side `~/homelab/docs/changes.log` is the operational history record.

Architecture records describe intent, design, and decision-making principles.

Standards records describe expected engineering behavior.

Infrastructure records describe current state.

AI context files summarize the current state for assistant workflows.

## When to Update Documents

Update architecture documents when:

* A design principle changes
* A new platform capability is defined
* The long-term direction changes
* A major decision needs explanation

Update standards documents when:

* A repeatable engineering expectation changes
* A collaboration or implementation rule changes
* A recurring source of engineering friction needs a durable workflow fix
* A quality bar becomes important enough to enforce consistently

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
