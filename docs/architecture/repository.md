# Repository Architecture

## Purpose

The repository is the canonical engineering knowledge record for the Aiden Platform.

It preserves vision, architecture, standards, infrastructure, operations, roadmaps, Repository Objects, generated context, and engineering tools.

Every file and directory should have one clear responsibility.

---

## Repository Layers

```text
Vision
Architecture
Standards
Infrastructure
Operations
Roadmaps
Engineering Toolkit
```

### Vision

Explains why the platform exists and where it is going.

Canonical owner:

- `docs/vision.md`

### Architecture

Explains how the platform should be designed.

Primary owners:

- `docs/architecture/platform.md`
- `docs/architecture/capabilities.md`
- `docs/architecture/ai.md`
- `docs/architecture/ai-operating-model.md`
- `docs/architecture/knowledge-authority.md`
- `docs/architecture/repository.md`
- `docs/architecture/atlas.md`
- `docs/architecture/task-scoped-agent-context-compilation.md`
- `docs/architecture/school-learning.md`

Specialized architecture covers engineering, reasoning, Repository Objects, opportunities, infrastructure capabilities, artifacts, collaboration, and future systems.

### Standards

Define repeatable expectations and quality bars.

Current owner:

- `docs/standards/engineering-collaboration.md`

### Infrastructure

Describes current deployed state.

- `docs/infrastructure.md`
- `docs/infrastructure-gamer-pve.md`
- `docs/services.md`
- `docs/infrastructure-snapshot.md` as a generated summary

### Operations

Preserve active workflow and history.

- `docs/knowledge-promotion.md` as the repeatable manual Canonical Knowledge Promotion operating procedure
- `docs/change-session.md`
- `docs/change-schema.md`
- `docs/changes.log`
- `docs/changes/*.yml`

Knowledge Authority Architecture owns promotion principles and authority requirements. `docs/knowledge-promotion.md` owns the repeatable manual workflow that applies those requirements, preserving the distinction between architecture intent and operational procedure.

### Roadmaps

Describe likely future direction and sequencing.

- `docs/roadmaps/platform-strategy.md`
- `docs/roadmaps/ai-engineering.md`
- `docs/roadmaps/engineering-toolkit.md`

### Engineering Toolkit

Contains Atlas and supporting tools.

The primary interface is:

```text
./atlas <command>
```

Tools expose platform concepts and should not become hidden owners of repository facts.

---

## Repository Objects

Repository Objects are structured repository-native entities with identity and lifecycle.

Current examples include Engineering Opportunity Objects under `docs/opportunities/`.

Objects preserve structured candidates.

They are not automatically architecture, current mission, or committed work.

---

## Generated Content

Generated files summarize canonical records but do not replace them.

Examples:

- `docs/aiden-context.md`
- `docs/infrastructure-snapshot.md`

Generated artifacts must declare their sources, managing tool, and generated status.

---

## Source of Truth Hierarchy

GitHub is the canonical documentation source.

The repository is the canonical source of truth for Aiden Platform engineering knowledge.

Architecture documents define intent.

The hierarchy is:

1. Vision defines purpose and durable direction.
2. Architecture records describe intent and structural design.
3. Standards records describe expected engineering behavior.
4. Current Mission defines active engineering work.
5. Infrastructure records describe current implementation and state.
6. Operations records describe change evidence and history.
7. Roadmaps describe likely future direction and sequencing.
8. Repository Objects preserve structured candidates and lifecycle state.
9. Generated context summarizes canonical documentation and never replaces it.
10. Git history records repository evolution.
11. Live verification resolves current operational reality.

Conversation context may explain intent but does not replace canonical repository knowledge.

---

## Canonical Ownership Rules

- Purpose and long-term direction belong in `docs/vision.md`.
- Platform structure belongs in `docs/architecture/platform.md`.
- Capability taxonomy belongs in `docs/architecture/capabilities.md`.
- AI and Personal AI architecture belong in `docs/architecture/ai.md`.
- Recurring model, provider, deployment, and AI-use decisions belong in `docs/architecture/ai-operating-model.md`.
- Knowledge authority, provenance, and promotion belong in `docs/architecture/knowledge-authority.md`.
- Deterministic compilation of bounded, task-specific generated context packages and their authority, selection, provenance, size, validation, and consumer boundaries belongs in `docs/architecture/task-scoped-agent-context-compilation.md`.
- The bounded School Learning workflow, local course-data contract, manual approved-AI handoff, and generated local views belong in `docs/architecture/school-learning.md`.
- Personal course materials, answers, learning history, and generated personal views remain outside the engineering repository. The repository owns School Learning architecture and implementation, not personal school data.
- The repeatable manual knowledge-promotion workflow belongs in `docs/knowledge-promotion.md`.
- Strategic sequencing belongs in `docs/roadmaps/platform-strategy.md`.
- Active work belongs in `docs/current-mission.md`.
- Current deployment belongs in infrastructure records.
- Repeatable behavior belongs in standards.
- Change evidence belongs in operations.
- Candidate work belongs in roadmaps or Repository Objects.
- Generated summaries remain derived.

Reference the canonical owner instead of duplicating full content.

---

## Document Registration

New canonical documents should be integrated through:

1. Creation.
2. Repository Architecture registration.
3. Documentation Map registration.
4. Atlas document definition or repository metadata.
5. Validation.
6. Repository Synchronization Reasoning.
7. Engineering Review.
8. Commit and push.

Human judgment decides whether a document should exist.

---

## Placement Rules

- Durable purpose belongs in Vision.
- Durable design belongs in Architecture.
- Repeatable expectations belong in Standards.
- Current implementation belongs in Infrastructure.
- Change evidence belongs in Operations.
- Future sequencing belongs in Roadmaps.
- Structured lifecycle entities belong in registered Repository Object locations.
- Helper software belongs in `tools/`.
- Rebuildable summaries belong in generated files.

Identify canonical responsibility before creating another overlapping document.

---

## Repository Health Standard

A healthy repository should make it easy to answer:

- Why does the platform exist?
- How is it structured?
- Which capabilities does it develop?
- What remains human-owned?
- What currently exists?
- What changed?
- What is active now?
- What may happen next?
- Which evidence supports the conclusion?
- Which tool or workflow owns the next action?

---

## Future Direction

The repository should evolve as the engineering knowledge system for the Aiden Platform through repository-owned metadata, search, impact analysis, reliable artifacts, bounded task context, versioned skills, human-reviewed knowledge promotion, and clearer roadmap relationships.

It should become more capable without becoming the platform's primary outcome.
