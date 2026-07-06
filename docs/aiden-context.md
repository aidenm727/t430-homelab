# Aiden Context

Generated: 2026-07-06

## Purpose

This file is an AI-readable context packet for the homelab project.

It summarizes the current state, active priorities, and operating rules so an AI assistant can quickly understand where the project stands.

## Current Mission

### Phase

Engineering Opportunity Intelligence

---

### Mission

Continue evolving Atlas into the primary deterministic engineering interface for the Aiden Platform.

The immediate objective is to extend Atlas beyond understanding the current engineering state into understanding future engineering opportunities.

Atlas should become capable of discovering, capturing, evaluating, preserving, prioritizing, and eventually scheduling engineering opportunities from repository knowledge, engineering reasoning, engineering sessions, architectural analysis, and future capability reasoning.

This phase establishes Engineering Opportunity Intelligence as the next reusable platform capability that expands Atlas from understanding engineering reality into understanding engineering possibility.

---

### Current Focus

- Design Engineering Opportunity Intelligence.
- Continue strengthening reusable platform capabilities over command-specific logic.
- Preserve engineering opportunities as canonical repository knowledge rather than conversational memory.
- Continue reducing drift between architecture, implementation, documentation, generated context, and AI-assisted engineering.
- Improve Atlas's ability to deliberately guide its own long-term evolution.

---

### Current Priorities

1. Design Engineering Opportunity Intelligence.
2. Design the Engineering Opportunity lifecycle.
3. Design canonical repository storage for engineering opportunities.
4. Design Engineering Opportunity Review.
5. Capture engineering opportunities discovered during engineering sessions.
6. Continue strengthening shared reasoning and interpretation capabilities.

---

### Recently Completed

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

- Large infrastructure expansion
- New self-hosted services
- Major hardware changes
- Premature local AI deployment
- Building large end-user applications
- Feature development without architectural justification

---

### Current Status

The platform now contains:

- Repository Knowledge
- Repository Reasoning
- Engineering Intelligence
- Engineering Interpretation
- Engineering Review
- Mission Advancement Reasoning
- Milestone Completion Reasoning
- Repository Validation
- Repository Synchronization Reasoning
- Deterministic engineering startup
- Canonical engineering architecture

Engineering Review is now the canonical engineering checkpoint for beginning implementation work.

The next architectural objective is enabling Atlas to understand not only the current engineering state, but also future engineering opportunities.

---

### Next Milestone

Design Engineering Opportunity Intelligence.

Engineering opportunities should become first-class engineering objects that can be:

- Captured
- Reviewed
- Accepted
- Architected
- Scheduled
- Implemented
- Completed

Engineering opportunities should eventually originate from multiple capability producers, including:

- Engineering sessions
- Repository inspection
- Architecture analysis
- Documentation analysis
- Repository consolidation analysis
- Capability maturity analysis
- Future reasoning capabilities
- Human engineering ideas

Engineering Opportunity Intelligence should evaluate, organize, prioritize, and preserve these opportunities as reusable repository knowledge.

---

### Success Criteria

The current phase is successful when:

- Engineering opportunities become a first-class platform capability.
- Engineering opportunities are preserved as canonical repository knowledge.
- Atlas can surface engineering opportunities without relying on conversational memory.
- Engineering opportunities have a deterministic lifecycle.
- Future engineering sessions naturally build upon previously captured opportunities.
- Engineering Opportunity Intelligence integrates cleanly with Repository Knowledge, Repository Reasoning, Engineering Intelligence, Engineering Interpretation, and Engineering Review.
- Atlas becomes increasingly capable of identifying high-leverage engineering investments before implementation begins.

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

- 2026-06-26 — Prototype Aiden engineering toolkit
- 2026-06-24 — Add gamer-pve node monitoring
- 2026-06-24 — Improve recent changes ordering
- 2026-06-24 — Add recent changes to generated AI context
- 2026-06-24 — Generate infrastructure snapshot from context tool

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
