# Platform Architecture

## Purpose

This document defines the structural architecture of the Aiden Platform.

The platform is an ecosystem of shared foundations and human agency domains.

Shared foundations provide reusable abilities.

Human agency domains apply those abilities to meaningful areas of life.

The platform's purpose and durable principles are defined in `docs/vision.md`.

---

## Architectural Model

```text
Aiden Platform
|
|-- Platform Foundations
|   |-- Platform Direction and Governance
|   |-- Engineering and Evolution
|   |-- Knowledge and Context
|   |-- Artificial Intelligence
|   |-- Automation and Integration
|   |-- Infrastructure and Operations
|   |-- Security, Privacy, and Resilience
|   `-- Interaction and Experience
|
`-- Human Agency Domains
    |-- Learning and Research
    |-- Health and Wellbeing
    |-- Economic Agency
    |-- Personal Operations
    `-- Creativity and Expression
```

The model is layered rather than flat because infrastructure, engineering, AI, interfaces, services, and life domains have different responsibilities.

---

## Platform Foundations

### Platform Direction and Governance

Keeps the platform intentional, coherent, human-owned, and aligned with long-term goals.

Responsibilities include vision, principles, capability architecture, strategic priorities, authority boundaries, technology adoption criteria, AI governance, and periodic recalibration.

### Engineering and Evolution

Provides the ability to design, implement, verify, document, synchronize, and improve the platform deliberately.

Responsibilities include architecture, Atlas, repository reasoning, current missions, Engineering Opportunities, validation, review, engineering environment management, and controlled agentic engineering.

Engineering is the evolution engine of the platform, not its primary human outcome.

### Knowledge and Context

Preserves, organizes, retrieves, explains, and applies meaningful knowledge.

Responsibilities include canonical platform knowledge, personal knowledge, documentation, research provenance, search, retrieval, context generation, memory boundaries, decision records, and knowledge promotion.

Storage preserves bytes.

Knowledge and Context makes information understandable and usable.

### Artificial Intelligence

Uses AI deliberately to improve reasoning, learning, engineering, creation, planning, research, and decision support.

Responsibilities include model evaluation, hosted and local AI, provider portability, Personal AI, context use, bounded agents, evidence, human approval boundaries, and sensitive-data handling.

AI is cross-cutting.

It may strengthen every other capability, but it does not own the human domains it supports.

### Automation and Integration

Connects systems and makes repeatable workflows reliable.

Responsibilities include APIs, connectors, scheduled and event-driven workflows, data movement, notifications, synchronization, approval points, and transparent execution records.

Automation should remove friction without removing awareness or control.

### Infrastructure and Operations

Provides reliable execution environments and operates them responsibly.

Responsibilities include compute, storage, networking, access, observability, backups, recovery, workstations, development environments, servers, virtualization, cloud resources, local AI compute, and service operations.

The homelab is one infrastructure environment.

Infrastructure supports the platform; it is not the platform itself.

### Security, Privacy, and Resilience

Protects the owner, the platform, its data, and continued operation.

Responsibilities include identity, access, secrets, data classification, privacy, encryption, device and service security, backups, incident response, provider risk, safe automation, portability, and continuity.

### Interaction and Experience

Exposes platform capabilities through understandable and useful human interfaces.

Responsibilities include web, desktop, mobile, conversation, voice where useful, dashboards, search, notifications, briefings, engineering interfaces, accessibility, review, and approval surfaces.

AidenOS belongs within this foundation.

---

## Human Agency Domains

### Learning and Research

Improves understanding, skill development, source evaluation, research, project-based learning, industry intelligence, and awareness without information overload.

### Health and Wellbeing

Improves health-related organization, nutrition, fitness, recovery, sleep, records, and evidence-informed decision support while preserving appropriate professional and human judgment.

### Economic Agency

Improves valuable skills, income, professional leverage, personal finance, business experimentation, and economic independence.

Subdomains:

- Career and Professional Development.
- Personal Finance.
- Business and Entrepreneurship.

### Personal Operations

Improves everyday scheduling, communication, travel, household workflows, documents, purchases, routines, maintenance, personal services, and planning.

### Creativity and Expression

Improves creative practice, experimentation, publishing, music, writing, visual work, media, software creation, and personal voice.

---

## Major Platform Systems

### Repository

The GitHub repository is the canonical engineering knowledge record.

It owns architecture, standards, missions, roadmaps, infrastructure records, operations, Repository Objects, and engineering tools.

### Atlas

Atlas is the deterministic engineering control plane.

Atlas helps humans and AI systems understand repository state, apply engineering contracts, verify changes, and evolve the platform deliberately.

Atlas is not the general personal assistant.

### Personal AI

Personal AI is the cross-cutting intelligence subsystem built from Artificial Intelligence, Knowledge and Context, Automation and Integration, Security, and Interaction capabilities.

It may support engineering and everyday life through shared knowledge, context, reasoning, learning, planning, and bounded action.

Personal AI is not one model and is not synonymous with AidenOS.

### AidenOS

AidenOS is the evolving interaction and experience environment through which the owner accesses, coordinates, and understands platform capabilities.

It may include dashboards, conversations, search, briefings, notifications, engineering interfaces, and domain workflows.

AidenOS is not the entire Aiden Platform.

### Infrastructure Environments

Infrastructure environments include the homelab, workstation, WSL environment, cloud services, networking, storage, and future devices.

They provide execution and operations but do not determine platform identity.

---

## Capability and Implementation Boundaries

A capability is something the platform should be able to do.

A system composes capabilities into a coherent responsibility.

A service provides a deployed function.

A tool supports a workflow or implementation.

Examples:

- Artificial Intelligence is a capability.
- Personal AI is a system.
- A hosted model endpoint is a service.
- A model-specific client is a tool.

- Engineering and Evolution is a capability.
- Atlas is a system.
- GitHub is a hosted service used by the repository workflow.
- `./atlas validate` is an interface.

---

## Cross-Cutting Rules

- High-impact decisions remain human-owned.
- Human domains reuse shared foundations instead of creating isolated stacks.
- Capabilities should survive provider and model changes.
- Canonical knowledge, generated context, execution records, and candidate findings remain distinguishable.
- Automation and agents require visible scope, permissions, evidence, and approval.
- Manual workflows may precede automation.
- Architecture and important actions remain inspectable.
- Complexity is justified only when it creates durable leverage.

---

## Evolution Model

Vision and capability architecture guide system design; roadmaps and
Engineering Opportunities preserve possible work. Explicit owner decisions
select and authorize bounded checkpoints.

`docs/architecture/engineering-lifecycle.md` owns the implementation,
verification, independent review, candidate acceptance, and separately
authorized publication or deployment lifecycle.
`docs/standards/engineering-collaboration.md` owns its tiered assurance and
authority gates.

Engineering Opportunities preserve possibilities.

Roadmaps organize direction.

`docs/current-state.json` owns typed active state. `docs/current-mission.md`
is its human-readable companion; machine-readable state wins on conflict.
Neither record grants permission.

Architecture owns durable design.

---

## Canonical Relationships

- `docs/vision.md` explains why the platform exists.
- `docs/architecture/capabilities.md` defines stable capability identities.
- `docs/architecture/ai.md` defines Artificial Intelligence and Personal AI.
- `docs/architecture/repository.md` defines repository authority.
- `docs/architecture/atlas.md` defines the engineering control plane.
- `docs/roadmaps/platform-strategy.md` defines dated sequencing.
