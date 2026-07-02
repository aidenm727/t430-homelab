# Repository Architecture

## Purpose

This document defines how the Aiden Platform repository is organized and why.

The repository is not just a place to store files. It is the canonical engineering record for the platform.

It contains the platform's architecture, infrastructure records, operational history, roadmaps, generated AI context, and engineering tools.

## Core Principle

Every file and directory should have one clear responsibility.

The repository should make the platform easier to understand, operate, document, and evolve.

## Repository Layers

The repository is organized into seven major layers:

    Vision
    Architecture
    Standards
    Infrastructure
    Operations
    Roadmaps
    Engineering Toolkit

## 1. Vision

Vision explains why the platform exists and where it is going.

Vision-level material should describe long-term intent, not implementation details.

Current documents:

* `docs/architecture/platform.md`

Future documents may include:

* `docs/vision.md`

## 2. Architecture

Architecture explains how the platform should be designed.

Architecture documents describe principles, relationships, responsibilities, and decision-making rules.

They should change deliberately and less frequently than infrastructure records.

Current documents:

* `docs/architecture/platform.md`
* `docs/architecture/engineering.md`
* `docs/architecture/capabilities.md`
* `docs/architecture/compute.md`
* `docs/architecture/ai.md`
* `docs/architecture/repository.md`
* `docs/architecture/atlas.md`

Architecture documents should not become service inventories.

## 3. Standards

Standards define how engineering work should be performed.

Standards documents describe expectations, rules, workflows, and quality bars that should be followed across the platform.

Current documents:

* `docs/standards/engineering-collaboration.md`

Standards should guide repeatable engineering behavior without becoming architecture, infrastructure records, or operational history.

## 4. Infrastructure

Infrastructure explains what currently exists.

Infrastructure documents describe hosts, services, networking, access, storage, backups, monitoring, and deployed workloads.

Current documents:

* `docs/infrastructure.md`
* `docs/infrastructure-gamer-pve.md`
* `docs/services.md`
* `docs/infrastructure-snapshot.md`

Infrastructure records should be updated when the real system changes.

## 5. Operations

Operations explains how the platform is safely changed.

Operational records capture change history, current work sessions, schemas, and procedures.

Current documents:

* `docs/change-session.md`
* `docs/change-schema.md`
* `docs/changes.log`
* `docs/changes/*.yml`

Operations should preserve the history of how the platform evolved.

## 6. Roadmaps

Roadmaps explain what the platform may improve next.

Roadmaps are expected to change more frequently than architecture documents.

They should capture planned or possible work without pretending that all ideas are final architecture.

Current documents:

* `docs/roadmaps/ai-engineering.md`
* `docs/roadmaps/engineering-toolkit.md`

Roadmaps should guide future work while remaining flexible.

## 7. Engineering Toolkit

The engineering toolkit contains software that helps build, understand, document, and operate the platform.

Current tools:

* `tools/generate-context.py`
* `tools/homelab-change.py`
* `tools/aiden-context-loader.py`

The toolkit should reduce engineering friction.

It should expose platform concepts rather than forcing the owner to remember individual file paths.

Future toolkit direction may include a unified `aiden` CLI.

Possible future commands:

```text
atlas status
atlas context
atlas change
atlas docs
atlas roadmap
atlas doctor
```

## Generated Content

Some files are generated or partially generated artifacts.

Generated files summarize canonical records but do not replace them.

Examples:

* `docs/aiden-context.md`
* `docs/infrastructure-snapshot.md`

Generated files should clearly indicate when they should not be edited directly.

The canonical source should remain the architecture, standards, infrastructure, operations, and roadmap documents.

## Source of Truth Rules

Use this source-of-truth order when reasoning about the repository:

1. Architecture documents define intent.
2. Standards documents define expected engineering behavior.
3. Infrastructure documents define current implementation.
4. Operations documents define change history.
5. Roadmaps define planned improvements.
6. Generated AI context summarizes the current state.
7. Git history records the evolution of the project.

## Placement Rules

Use these rules when adding new files:

* Long-term design decisions belong in `docs/architecture/`.
* Engineering standards belong in `docs/standards/`.
* Current deployed system records belong in infrastructure documentation.
* Change history belongs in `docs/changes/` and `docs/changes.log`.
* Future work belongs in `docs/roadmaps/`.
* Engineering helper software belongs in `tools/`.
* Generated context belongs in clearly marked generated files.

When unsure, prefer creating a small focused document rather than expanding an unrelated one.

## Future Direction

The repository should evolve toward becoming the engineering operating system for the Aiden Platform.

Future improvements may include:

* A unified engineering CLI
* Better generated AI context
* Documentation consistency checks
* Roadmap-aware planning
* Engineering state summaries
* AI-assisted documentation review
* Search and retrieval across architecture, changes, and infrastructure

The long-term goal is for the repository to preserve understanding as the platform grows.

## Repository Design Standard

A healthy repository should make it easy to answer:

* Why does the platform exist?
* How is it designed?
* What currently exists?
* What changed recently?
* What is being worked on now?
* What should happen next?
* Which tools support the engineering workflow?

The repository should reduce confusion, prevent duplicated work, and help both humans and AI assistants start from an accurate understanding of the platform.
