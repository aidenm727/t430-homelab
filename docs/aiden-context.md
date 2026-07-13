# Aiden Context

Generated: 2026-07-13

## Purpose

This file is an AI-readable context packet for the homelab project.

It summarizes the current state, active priorities, and operating rules so an AI assistant can quickly understand where the project stands.

## Current Mission

### Phase

Engineering Opportunity Intelligence

---

### Mission

Continue evolving Atlas into the primary deterministic engineering interface for the Aiden Platform.

The immediate objective is to extend the completed Engineering Opportunity Assessment foundation with structured repository evidence and explicit relationship inputs.

This milestone should strengthen Repository Knowledge and Repository Reasoning without introducing semantic comparison, opaque scoring, automatic lifecycle mutation, permanent assessment storage, or command-specific evaluation logic.

---

### Current Focus

- Build the Engineering Opportunity Evidence foundation.
- Preserve explicit dependencies, related opportunities, related documents, and evidence in the normalized repository-object representation.
- Make those inputs available to reusable Engineering Opportunity Assessment reasoning.
- Validate explicit references deterministically.
- Produce source-backed findings for unresolved opportunity and document references.
- Keep canonical objects separate from rebuildable assessment outputs.
- Preserve human authority over opportunity lifecycle changes.

---

### Current Priorities

1. Extend the normalized Engineering Opportunity Object representation with structured dependencies, related opportunities, related documents, and evidence.
2. Support the bounded YAML structures required by canonical opportunity objects without introducing a general-purpose configuration framework.
3. Preserve explicit evidence and relationship inputs during repository-object loading.
4. Add reusable assessment facts for explicit dependencies, related opportunities, related documents, and evidence.
5. Validate referenced Engineering Opportunity identifiers against the discovered opportunity inventory.
6. Validate referenced repository documents against canonical repository paths.
7. Produce deterministic findings, blockers, and unresolved questions for missing or inconsistent explicit references.
8. Add focused tests for valid references, missing opportunity targets, missing document targets, and objects without optional references.
9. Establish deterministic milestone-completion evidence for the evidence foundation.

---

### Recently Completed

- Engineering Opportunity Assessment foundation
- Reusable Engineering Opportunity Assessment data model
- Deterministic Engineering Opportunity object-quality reasoning
- Assessment tests for valid, incomplete, and inconsistent objects
- Engineering Opportunity Assessment milestone recognition
- Design Engineering Opportunity Intelligence
- Engineering Opportunity Assessment architecture
- Engineering Opportunity Object architecture and lifecycle
- Engineering Opportunity repository ownership
- Initial Engineering Opportunity Object inventory
- Atlas opportunities interface
- Engineering Opportunity design milestone recognition
- Repository Synchronization Reasoning
- Mission Advancement Reasoning
- Milestone Completion Reasoning
- Engineering Intelligence
- Engineering Interpretation
- Engineering Review
- Structured milestone criteria
- Repository validation
- Repository synchronization
- Repository impact analysis
- Engineering-state awareness
- Deterministic engineering startup
- Context generation workflows

---

### Current Non-Priorities

- Semantic duplicate and overlap determination
- Inferred opportunity relationships
- Scope classification
- Portfolio-wide prioritization
- Strategic-value scoring
- Broad autonomous candidate-opportunity discovery
- Automatic lifecycle mutation
- Automatic mission or roadmap creation
- Permanent assessment artifact storage
- Moving assessment logic into Atlas commands
- Dependence on a specific AI model or provider
- Large infrastructure expansion
- New self-hosted services
- Major hardware changes
- Building large end-user applications

---

### Current Status

The Engineering Opportunity Assessment foundation is implemented and recognized by Atlas with high confidence.

The repository now contains:

- A reusable structured assessment data model
- Explicit separation between repository facts, derived findings, and recommendations
- Deterministic identity, required-field, lifecycle, placement, and basic evidence-presence checks
- Evidence-backed findings with confidence, blockers, and unresolved questions
- Bounded recommendations that preserve human lifecycle authority
- Focused assessment tests
- Deterministic milestone-completion reasoning

The current repository-object loader still preserves only a limited subset of canonical Engineering Opportunity Object fields. Explicit dependencies, related opportunities, related documents, and structured evidence are not yet available as reusable reasoning inputs.

The next responsible step is therefore to establish structured evidence and explicit-reference support before implementing scope classification, relationship inference, duplicate detection, prioritization, or downstream Engineering Intelligence composition.

---

### Next Milestone

Build Engineering Opportunity Evidence Foundation.

Extend the repository-object and assessment layers so existing Engineering Opportunity Objects can expose and validate explicit dependencies, related opportunities, related documents, and evidence.

The first evidence evaluator should produce:

- Source-backed facts for explicit evidence and references
- Deterministic validation of referenced opportunity identifiers
- Deterministic validation of referenced repository document paths
- Findings for missing or inconsistent explicit references
- Explainable confidence
- Blockers and unresolved questions
- A bounded recommendation that does not mutate lifecycle state

This milestone should not infer semantic relationships, identify duplicates from language similarity, classify strategic value, rank the opportunity portfolio, discover new opportunities autonomously, or modify canonical opportunity objects.

---

### Success Criteria

The milestone is complete when:

- The normalized Engineering Opportunity Object representation includes structured dependencies, related opportunities, related documents, and evidence.
- Repository-object loading preserves the bounded YAML structures used by those fields.
- Existing opportunity objects remain human-readable and canonical.
- Engineering Opportunity Assessments can expose explicit evidence and references as source-backed facts.
- Referenced Engineering Opportunity identifiers are validated against discovered repository objects.
- Referenced repository document paths are validated against repository reality.
- Missing opportunity or document targets produce explicit deterministic findings rather than loader failures or silent omission.
- Objects without optional evidence or references remain valid and assessable.
- Findings include supporting evidence and explainable confidence.
- Assessment reasoning remains independent of Atlas command rendering.
- No assessment path automatically creates, edits, moves, merges, accepts, rejects, schedules, or closes an opportunity.
- Tests cover valid references, missing opportunity targets, missing document targets, and absent optional references.
- Atlas can recognize completion of the evidence foundation from concrete implementation and test evidence.

## Infrastructure Snapshot

> Generated context artifact.
> Do not edit directly; update canonical infrastructure records instead.

### Production Host

t430-beast

* Role: Production services host
* OS: Ubuntu Server 24.04.4 LTS
* LAN IP: 10.0.0.136

Responsibilities:

* Pi-hole
* Traefik
* Homepage
* Grafana
* Prometheus
* Loki
* Alloy
* Uptime Kuma
* Vaultwarden
* Backup infrastructure

### Virtualization Host

gamer-pve

* Role: Proxmox virtualization host
* OS: Proxmox VE 9
* LAN IP: 10.0.0.178
* Tailscale IP: 100.80.182.80

Hardware:

* Ryzen 5 2600
* 16 GB DDR4
* RTX 4060-class GPU

Storage:

* 500 GB SSD (Proxmox OS)
* 1 TB NVMe SSD
* 2 TB SATA SSD

Purpose:

* VM hosting
* LXC hosting
* Immich
* AI experimentation
* Future workloads

### Active Workloads

#### LXC 200 - Immich

* Debian 12
* Docker Engine
* Docker Compose
* 128 GB root disk
* LAN IP: 10.0.0.132

### Active Services

* Pi-hole
* Traefik
* Homepage
* Uptime Kuma
* Grafana
* Prometheus
* Loki
* Alloy
* Vaultwarden
* Immich

## Recent Changes

- 2026-06-23 — Add NVMe Proxmox Storage Pool
- 2026-06-23 — Improve change capture workflow
- 2026-06-26 — Prototype Aiden engineering toolkit
- 2026-06-24 — Improve recent changes ordering
- 2026-06-23 — Homelab documentation and AI context system v1

## Authoritative Sources

- docs/infrastructure.md
- ~/homelab/docs/changes.log
- Git history
- Live infrastructure state

## Operational Rules

- Deploy / Configure
- Verify functionality
- Document immediately
- Commit and push from the local machine
- Never commit secrets

## Current Priorities

1. Create and document the first VM deployment on gamer-pve
2. Continue improving the infrastructure documentation model
3. Build the Aiden Context generation workflow
4. Explore how ChatGPT Projects, source files, and future Aiden OS assistants should share context

## Known Constraints

- t430-beast should remain the stable production services host
- gamer-pve should be used for virtualization, experimentation, and heavier workloads
- changes.log currently lives only on the server
- GitHub documentation remains the canonical public documentation source

## Active Change Session

# Homelab Change Session

Started: 2026-06-26 12:02:06

## Change Title

Prototype Aiden engineering toolkit

## Change Type

automation

## Intent
- [2026-06-26 12:02:06] Begin organizing existing repository tools into a future Aiden engineering toolkit

## Notes
- [2026-06-26 12:07:09] Updated aiden-context-loader.py to summarize engineering state instead of dumping full source documents

## Verification
- [2026-06-26 12:07:09] Ran python3 tools/aiden-context-loader.py and verified it reports git status, active change session, recent changes, architecture docs, context docs, roadmaps, tools, and next step

## Documentation Outputs
- [2026-06-26 12:07:09] Updated tools/aiden-context-loader.py as the first prototype of the Aiden engineering toolkit



## Next Milestone

Deploy the first VM on gamer-pve and document the VM architecture using the new documentation workflow.
