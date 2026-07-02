# Repository Metadata Architecture

## Purpose

Repository metadata provides machine-readable descriptions of important repository artifacts.

Its purpose is to let Atlas understand repository documents, relationships, ownership, generated artifacts, and engineering responsibilities without hardcoding that knowledge directly in Python.

## Core Principle

Repository knowledge should live in the repository.

Atlas should load repository metadata from structured files, then reason over that metadata.

Python should define behavior.

Repository metadata should define repository facts.

## Problem

Atlas currently stores document definitions in Python.

This works for early implementation, but it creates long-term friction:

- Adding a document requires editing Python.
- Repository facts are separated from repository documentation.
- Metadata is harder for humans to review.
- Atlas knowledge does not yet feel like a first-class repository asset.

As the repository grows, document metadata should become part of the repository itself.

## Metadata Responsibilities

Repository metadata should describe:

- Document path
- Document layer
- Purpose
- Capability
- Canonical or generated status
- Related documents
- Generated artifact ownership
- Source documents for generated artifacts
- Managing tool or workflow
- Tags
- Current status

## Proposed Location

Repository metadata should eventually live under:

    docs/metadata/

Example files:

    docs/metadata/platform.yml
    docs/metadata/atlas.yml
    docs/metadata/engineering-collaboration.yml
    docs/metadata/infrastructure.yml
    docs/metadata/generated-context.yml

Metadata files should be small, reviewable, and organized around repository artifacts or closely related groups of artifacts.

## Initial Metadata Shape

A document metadata entry should support fields such as:

    path
    title
    layer
    purpose
    capability
    canonical
    generated
    status
    tags
    related
    generated_from
    managed_by

The initial schema should remain intentionally small.

Atlas should not require metadata fields that are not yet useful.

## Atlas Loading Model

Atlas should load repository knowledge in this order:

1. Discover repository documents from the filesystem.
2. Load structured metadata from docs/metadata.
3. Attach metadata to discovered documents.
4. Report documents without metadata.
5. Expose enriched document knowledge to reasoning capabilities.

Discovery should determine what exists.

Metadata should explain what those artifacts mean.

Reasoning should evaluate implications.

## Relationship to Document Definitions

The current Python document definitions should be treated as a transitional implementation.

Over time, Atlas should move from:

    Python dictionary document definitions

to:

    Repository metadata files loaded by Atlas

The migration should be incremental.

The first implementation may keep the existing Python model while introducing metadata loading for new or migrated documents.

## Design Constraints

Repository metadata should be:

- Human-readable
- Version controlled
- Easy to review in pull requests
- Deterministic for Atlas to load
- Separate from generated context
- Small enough to maintain manually
- Strict enough to support validation later

## Non-Responsibilities

Repository metadata should not:

- Replace the documents themselves
- Store secrets
- Store long-form architecture
- Become generated AI context
- Duplicate entire document contents
- Make architectural decisions automatically

Metadata describes repository artifacts.

It does not replace human judgment or canonical documentation.

## Atlas Reasoning Benefits

Repository metadata enables Atlas to reason about:

- Missing document definitions
- Stale generated artifacts
- Cross-document relationships
- Capability ownership
- Standards applicability
- Documentation completeness
- Repository synchronization
- Change impact

This strengthens the Repository Knowledge Layer before expanding Repository Reasoning.

## Initial Implementation Direction

The first implementation should be conservative.

Recommended sequence:

1. Add repository metadata architecture.
2. Add metadata awareness to the repository architecture.
3. Add Standards to existing Atlas document definitions as a short-term bridge.
4. Design a minimal metadata schema.
5. Create the first docs/metadata prototype.
6. Teach Atlas to load metadata.
7. Gradually migrate Python document definitions into metadata files.

This avoids a large refactor while moving the repository toward first-class machine-readable knowledge.
