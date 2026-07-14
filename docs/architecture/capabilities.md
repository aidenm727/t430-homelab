# Platform Capability Architecture

## Purpose

This document defines the durable capability taxonomy of the Aiden Platform.

A capability is something the platform should be able to do independently of the specific tool, service, provider, model, or hardware used to implement it.

The model has two layers:

1. Platform Foundations provide reusable abilities.
2. Human Agency Domains describe where those abilities create meaningful value.

---

## Platform Foundation Identities

| Capability ID | Display Label |
| --- | --- |
| `platform-governance` | Platform Direction and Governance |
| `engineering-evolution` | Engineering and Evolution |
| `knowledge-context` | Knowledge and Context |
| `artificial-intelligence` | Artificial Intelligence |
| `automation-integration` | Automation and Integration |
| `infrastructure-operations` | Infrastructure and Operations |
| `security-privacy-resilience` | Security, Privacy, and Resilience |
| `interaction-experience` | Interaction and Experience |

### `platform-governance`

Owns vision, principles, capability architecture, strategic priorities, authority boundaries, governance, and recalibration.

### `engineering-evolution`

Owns repeatable platform design, implementation, verification, documentation, synchronization, review, missions, Atlas, and Engineering Opportunities.

### `knowledge-context`

Owns documentation, personal knowledge, provenance, research sources, retrieval, context generation, memory boundaries, and knowledge promotion.

### `artificial-intelligence`

Owns model evaluation, hosted and local AI, Personal AI, context use, bounded agents, evidence, and provider portability.

### `automation-integration`

Owns APIs, connectors, orchestration, notifications, synchronization, scheduled work, and approval-aware automation.

### `infrastructure-operations`

Owns compute, storage, networking, observability, backups, workstations, cloud resources, virtualization, services, recovery, and operations.

### `security-privacy-resilience`

Owns identity, access, secrets, privacy, data classification, encryption, incident response, provider risk, recovery, portability, and safe automation.

### `interaction-experience`

Owns AidenOS, dashboards, conversations, search, briefings, notifications, mobile and desktop surfaces, and review interfaces.

---

## Human Agency Domain Identities

| Capability ID | Display Label |
| --- | --- |
| `learning-research` | Learning and Research |
| `health-wellbeing` | Health and Wellbeing |
| `economic-agency` | Economic Agency |
| `personal-operations` | Personal Operations |
| `creativity-expression` | Creativity and Expression |

### `learning-research`

Improves understanding, skill development, research, source evaluation, curricula, and awareness.

### `health-wellbeing`

Improves health organization, nutrition, fitness, recovery, sleep, and evidence-informed support.

### `economic-agency`

Improves career capability, professional leverage, personal finance, business experimentation, and economic independence.

Subdomains:

- Career and Professional Development.
- Personal Finance.
- Business and Entrepreneurship.

### `personal-operations`

Improves scheduling, communication, travel, household workflows, documents, routines, and personal services.

### `creativity-expression`

Improves creative practice, experimentation, publishing, music, writing, visual work, media, software creation, and personal voice.

---

## Capability Relationships

Platform Foundations support all Human Agency Domains.

A workflow may have one primary capability and several secondary implications.

A nutrition workflow may use:

- `knowledge-context`
- `artificial-intelligence`
- `automation-integration`
- `security-privacy-resilience`
- `interaction-experience`
- `health-wellbeing`
- `personal-operations`

A career intelligence workflow may use:

- `learning-research`
- `economic-agency`
- `knowledge-context`
- `artificial-intelligence`
- `automation-integration`

---

## Systems and Implementations

| Concept | Architectural Position |
| --- | --- |
| Aiden Platform | Entire capability ecosystem |
| Atlas | Engineering and Evolution system |
| GitHub repository | Canonical engineering knowledge implementation |
| Personal AI | Cross-cutting AI system |
| AidenOS | Interaction and Experience system |
| Homelab | Infrastructure implementation |
| Laptop and WSL | Engineering and infrastructure implementation |
| Immich and Vaultwarden | Services supporting human domains |
| ChatGPT Project | Hosted AI and context interface |
| Local model runtime | AI and infrastructure implementation |

---

## Legacy Capability Compatibility

The previous map defined nine flat identities.

Those identifiers may still appear in Engineering Opportunity Objects, tests, Atlas reasoning, infrastructure records, and documentation.

They remain recognized temporarily as compatibility identifiers but are no longer canonical top-level capabilities.

| Legacy ID | Canonical Destination | Compatibility Meaning |
| --- | --- | --- |
| `compute` | `infrastructure-operations` | Compute specialization |
| `storage` | `infrastructure-operations` | Storage specialization |
| `networking-access` | `infrastructure-operations` and `security-privacy-resilience` | Network operation and access-control implications |
| `observability` | `infrastructure-operations` | Operational visibility specialization |
| `automation` | `automation-integration` | Direct alias during migration |
| `knowledge-documentation` | `knowledge-context` and `engineering-evolution` | Knowledge ownership with engineering-documentation implications |
| `engineering` | `engineering-evolution` | Direct alias during migration |
| `personal-services` | Domain-specific classification | Services are implementations rather than one capability |
| `ai-aiden-os` | `artificial-intelligence` and `interaction-experience` | Former combined identity split into two foundations |

Compatibility rules:

- Existing object identifiers and lifecycle state must not change automatically.
- Atlas may resolve legacy values through explicit mappings.
- A legacy value may resolve to one capability, multiple implications, or an ambiguity requiring review.
- New architecture and new objects should use canonical identifiers.
- Compatibility support must remain visible and testable.
- Removal requires reviewed migration evidence.
- Capability migration is not opportunity duplication or lifecycle mutation.

---

## Capability Maturity

Capability maturity evaluates durable ability, not the existence of a related service.

### Level 0 — Not Established

Recognized but without a usable workflow or architecture.

### Level 1 — Experimental

Explored through manual workflows, prototypes, or early architecture.

### Level 2 — Operational

Provides repeatable value through an understandable workflow.

### Level 3 — Reliable

Documented, verified, recoverable, secure where applicable, and part of normal operation.

### Level 4 — Platform Native

Deeply integrated, reusable across systems, and improves other capabilities.

---

## Initial Strategic Assessment

| Capability | Initial Maturity | Basis |
| --- | ---: | --- |
| Platform Direction and Governance | Level 1 | Vision and governance are becoming canonical. |
| Engineering and Evolution | Level 2 | Atlas and repository workflows are operational; consolidation remains. |
| Knowledge and Context | Level 2 | Engineering knowledge is strong; broader personal knowledge is early. |
| Artificial Intelligence | Level 1 | Hosted workflows are useful; operating rules and Personal AI remain early. |
| Automation and Integration | Level 2 | Infrastructure and context automation exist; cross-domain integration is limited. |
| Infrastructure and Operations | Level 2 | Core environments operate; storage and recovery continue to mature. |
| Security, Privacy, and Resilience | Level 2 | Strong practices exist; explicit platform-wide governance is incomplete. |
| Interaction and Experience | Level 0 | AidenOS is conceptual rather than operational. |
| Learning and Research | Level 1 | Assisted learning exists; durable workflows are not integrated. |
| Health and Wellbeing | Level 1 | Repeated assisted workflows exist; no platform capability is established. |
| Economic Agency | Level 1 | Career and finance planning occur; no integrated system exists. |
| Personal Operations | Level 1 | Useful services and workflows exist but remain fragmented. |
| Creativity and Expression | Level 1 | Creative practices exist; platform support remains informal. |

---

## Planning Rule

Future work should:

1. Identify the human outcome or platform responsibility.
2. Identify the primary canonical capability.
3. Identify secondary implications.
4. Determine whether an existing system already provides the capability.
5. Design architecture before introducing a major system.
6. Select an implementation only after the need is clear.
7. Define evidence that the capability improved.

A service should not be added only because it is interesting.

---

## Canonical Relationships

- `docs/vision.md` defines why these capabilities matter.
- `docs/architecture/platform.md` defines their structural relationship.
- `docs/architecture/ai.md` defines Artificial Intelligence and Personal AI.
- `docs/roadmaps/platform-strategy.md` defines sequencing.
- Engineering Opportunity Capability Alignment should consume this taxonomy through explicit compatibility rules.
