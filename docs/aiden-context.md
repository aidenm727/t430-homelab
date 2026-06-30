# Aiden Context

Generated: 2026-06-30

## Purpose

This file is an AI-readable context packet for the homelab project.

It summarizes the current state, active priorities, and operating rules so an AI assistant can quickly understand where the project stands.

## Current Mission

Phase: Engineering Platform Implementation

Current Focus:

- Build Atlas as the deterministic engineering interface for the Aiden Platform
- Strengthen the repository knowledge model
- Reduce friction between an idea and a well-engineered implementation
- Keep architecture, documentation, implementation, verification, commits, and AI context aligned

Current Priorities:

1. Build reusable Atlas capabilities before adding command-specific logic.
2. Use Atlas to discover, explain, and navigate repository knowledge.
3. Consolidate existing engineering tools into a coherent engineering workflow.
4. Strengthen validation and reasoning capabilities before expanding platform services.
5. Keep the ChatGPT Project environment synchronized with the repository.

Current Non-Priorities:

- Deploying new self-hosted services
- Expanding personal services
- Major infrastructure changes
- Local AI deployment
- Large Atlas feature batches

Current Status:

- The Aiden Platform architecture layer has been established.
- Engineering is defined as a first-class platform capability.
- Atlas architecture has been added and expanded.
- Atlas CLI supports state, doctor, next, docs, explain, missing, and open.
- Atlas has a shared engineering-state model.
- Atlas has repository discovery and document catalog capabilities.
- Atlas has metadata definitions for all discovered documents.
- Atlas can explain and open repository documents by engineering name.
- Existing tools include context generation, change logging, and prototype engineering-state loading.

Next Milestone:

Build higher-level Atlas reasoning capabilities on top of the Repository Knowledge Layer, beginning with document relationships, validation, and synchronization awareness.

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
