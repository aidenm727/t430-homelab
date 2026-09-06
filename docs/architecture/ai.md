# Artificial Intelligence Architecture

## Purpose

Artificial Intelligence is a first-class, cross-cutting foundation of the Aiden Platform.

Its purpose is to increase the owner's agency by improving reasoning, learning, engineering, research, knowledge use, planning, creation, and bounded automation.

AI is not a single application, subscription, model, or provider.

The architecture should allow providers to change without surrendering platform knowledge, identity, or authority.

The objective is not to automate life.

---

## Architectural Position

Artificial Intelligence supports other foundations and Human Agency Domains but does not own them.

- AI assists Learning and Research but does not own learning goals.
- AI assists Health and Wellbeing but does not make medical decisions.
- AI assists Economic Agency but does not own career, business, or financial commitments.
- AI assists Engineering and Evolution but does not own architecture or high-impact changes.
- AI may power AidenOS experiences but is not synonymous with AidenOS.

---

## Principles

- AI should improve capability rather than replace responsibility.
- Capabilities remain stable while models and providers change.
- Important outputs should expose sources, assumptions, uncertainty, and validation where practical.
- Providers should be replaceable without losing canonical knowledge.
- Recommendations, prepared changes, and executed actions remain distinguishable.
- Complexity should be proportionate to proven value.

The owner remains responsible for long-term direction, architecture, security-sensitive changes, important validation, personal data boundaries, automation authority, and consequential life decisions.

---

## Operational Architecture

This document owns durable Artificial Intelligence and Personal AI architecture.

Recurring operational decisions are owned by specialized architecture:

- `docs/architecture/ai-operating-model.md` defines task-based provider, model, deployment, evidence, and fallback decisions.
- `docs/architecture/knowledge-authority.md` defines authority classes, provenance, canonical ownership, and knowledge promotion.

The specialized documents apply this architecture without redefining its principles or system boundaries.

---

## Personal AI

Personal AI is the cross-cutting intelligence subsystem of the Aiden Platform.

It composes:

- Artificial Intelligence.
- Knowledge and Context.
- Automation and Integration.
- Security, Privacy, and Resilience.
- Interaction and Experience.
- Relevant Human Agency Domains.

It may provide research, synthesis, personal context, knowledge retrieval, tutoring, planning, engineering support, creative assistance, briefings, domain decision support, and bounded actions.

Personal AI is not one assistant persona.

It is a shared capability layer that may be exposed through multiple interfaces.

---

## AI Capability Areas

### Engineering Intelligence

Supports architecture, planning, implementation, debugging, documentation, repository reasoning, review, and controlled agentic workflows.

Atlas remains the deterministic engineering control plane.

### Knowledge Intelligence

Supports search, retrieval, synthesis, context generation, source comparison, memory augmentation, and knowledge promotion.

Generated context never becomes canonical automatically.

### Learning and Research Intelligence

Supports explanations, curricula, project-based learning, interview preparation, concept reinforcement, source discovery, evaluation, synthesis, and uncertainty tracking.

### Personal Decision Support

Supports health, finance, career, business, travel, planning, and other domains while preserving human commitments and judgment.

### Automation Intelligence

Supports preparation, orchestration, classification, reporting, and bounded execution with visible permission and evidence.

### Creative Intelligence

Supports ideation, critique, editing, experimentation, and production while preserving taste, authorship, and voice.

---

## Data Sensitivity

### Public

Information intentionally public or already broadly available.

May generally be used with approved hosted services.

### Ordinary Personal

Low-risk personal context whose disclosure would be inconvenient but not severely harmful.

Use should remain purposeful and provider-aware.

### Sensitive

Private communications, detailed location, educational records, unpublished work, personal finances, health, or similar information.

Use requires deliberate provider and retention review.

Local or minimized processing may be preferred.

### Highly Restricted

Passwords, API keys, private keys, tokens, recovery codes, highly sensitive identity data, or information that could directly compromise systems or safety.

Highly Restricted information must not be sent to general hosted AI systems or committed to the repository.

---

## Deployment Strategy

### Hosted AI

Provides frontier reasoning, research, multimodal understanding, writing, coding, and rapid access to new capabilities.

Tradeoffs include external dependency, cost, privacy, retention, and changing provider policy.

### Local AI

May provide privacy, control, offline operation, experimentation, and deep integration.

Tradeoffs include hardware cost, operational complexity, energy, maintenance, and potentially lower capability.

Local AI should be adopted because it improves a real capability.

### Hybrid AI

The long-term architecture is hybrid.

Assignment should consider capability, sensitivity, cost, latency, reliability, context size, tool access, operational burden, and local-control requirements.

Hybrid does not require automatic routing initially.

---

## Provider and Model Evaluation

Evaluate a model or tool against a defined task:

- Which capability improves?
- What is the result quality?
- What evidence supports that judgment?
- How reliable is tool use?
- Does it preserve scope?
- What context and data does it receive?
- What are retention and privacy terms?
- What is the cost and burden?
- Is a current capability already sufficient?
- Can the workflow move to another provider?

Product rankings are evidence, not architecture.

The operational selection contract is defined in `docs/architecture/ai-operating-model.md`.

---

## Context and Knowledge Authority

AI context should distinguish:

- Canonical knowledge.
- Generated context.
- Personal context.
- Temporary conversation.
- Execution records.
- Candidate findings.
- Completed actions.
- Unknown or conflicting information.

Canonical knowledge is reviewed and owned by its designated source.

Generated context is derived and rebuildable.

Candidate findings require review before promotion.

Conversation memory is useful but not automatically authoritative.

Detailed authority classes and the Canonical Knowledge Promotion Workflow are defined in `docs/architecture/knowledge-authority.md`.

---

## Recommendation and Action Boundaries

AI behavior should be distinguishable as:

1. Explain.
2. Recommend.
3. Prepare.
4. Execute bounded reversible work.
5. Request approval.
6. Perform a separately authorized high-impact action.

High-impact actions remain independently gated, including architecture changes, mission changes, production changes, destructive operations, credential access, financial commitments, external communications, publishing, repository pushes, and writable-scope expansion.

---

## Relationship to Atlas and AidenOS

Canonical repository owners own engineering state and contracts.
Atlas deterministically observes, validates, interprets, and presents them
within `docs/architecture/atlas.md` responsibilities. Atlas evidence grants no
task, implementation, publication, deployment, or external-write authority.

AI systems consume Atlas evidence rather than redefining repository state through conversational confidence.

AidenOS is the Interaction and Experience environment.

Personal AI may be a major part of AidenOS, but AidenOS should also expose deterministic tools, knowledge, services, and workflows that do not depend on AI.

AI and AidenOS therefore remain separate capability identities.

---

## Evaluation

AI workflows should be evaluated through correctness, usefulness, source quality, scope preservation, human correction, repair attempts, time saved, learning retained, decisions improved, authority compliance, and portability.

Evaluation should remain explainable rather than becoming one opaque universal score.

---

## Initial Direction

Near-term work should prioritize AI operating rules, data classification, provider evaluation, Personal AI boundaries, knowledge ownership, career and research intelligence, and manual proof of useful workflows.

The bounded task-context compilation library is implemented under
`docs/architecture/task-scoped-agent-context-compilation.md`, with structured
resources owned by `docs/task-context/index.md`. This does not establish a
general context CLI, production runtime, or Personal AI implementation.

Later work may include local AI experiments, additional context consumers,
task contracts, autonomy policy, versioned skills, execution evidence, bounded
repair loops, and AidenOS experiences. Personal AI implementation remains
deferred.

The platform should become progressively more capable without becoming progressively more dependent.
