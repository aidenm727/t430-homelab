# Aiden Context

Generated: 2026-07-31

## Purpose

This file is an AI-readable context packet for the Aiden Platform engineering repository.

It projects canonical active state, its human companion, and the existing infrastructure summary. It is generated and non-canonical.

## Canonical Active State

- Schema version: 1
- Effective date: 2026-07-31
- Phase: School Learning v0.1.1 Guided Study Handoff — Published
- Phase lifecycle: published
- Work selection: selected
- Selected checkpoint: Clean Foundation F1 — Canonical State, Authority, and Orientation
- Intentional idle: No
- Decision required: `clean-foundation-f1-publication-finalization` — Finalize the separately authorized publication of the owner-accepted Clean Foundation F1 candidate without selecting additional work.

### Blockers

- None

### Unknowns

- None

### Evidence

- `school-learning-v0-1-1-publication`: `docs/current-mission.md` at `0ffa8f5fe24d32d6bf32f1d866a882a3fea3176d` (records_phase)
- `school-learning-v0-1-1-architecture`: `docs/architecture/school-learning.md` at `9782eebec049b9b932cc583def499a44f1cbba2c` (defines_phase)

### Authority

- Task: external-not-established-by-repository-or-atlas
- Implementation: external-not-established-by-repository-or-atlas
- Publication: external-not-established-by-repository-or-atlas

Repository state and Atlas do not establish authority.

## Current Mission Companion

`docs/current-state.json` is the canonical typed active-state record. This
document is its short human-readable companion. Machine-readable state wins if
the two disagree.

### Phase

School Learning v0.1.1 Guided Study Handoff — Published

### Active State

The accepted and published School Learning phase remains current. Clean
Foundation F1 is selected and owner-accepted as implementation-complete. Its
separately authorized bounded publication finalization is the remaining current
boundary; F1 is not yet represented as published or operational.

Canonical state effective date: 2026-07-31.

### Mission Intent

Establish the Clean Foundation F1 state, authority, Atlas-readiness, and
repository-orientation foundation while preserving School Learning and
task-scoped context compilation behavior. Publish only the accepted F1
candidate and its bounded acceptance evidence, then finalize canonical state.

### Work Selection

- Status: Selected.
- Checkpoint: Clean Foundation F1 — Canonical State, Authority, and Orientation.
- Intentional idle: No.

### Next Milestone

Clean Foundation F1 — Canonical State, Authority, and Orientation

### Blockers

None recorded in canonical active state.

### Unknowns

None recorded in canonical active state.

### Current Publication Boundary

Owner acceptance is complete. Finalize the separately authorized bounded F1
publication without selecting another checkpoint. Canonical state does not
assert that F1 is already committed or present on `origin/main`; Git and fresh
remote verification own that fact.

### Authority Boundary

Repository state selects work but grants no task, implementation, publication,
deployment, or external-write authority. Atlas observes and explains state but
grants no authority. Current authority must come from explicit owner instruction
outside repository state, with implementation and publication authority bounded
separately. `AGENTS.md` is the primary repository-local authority-interpretation
contract.

### Evidence and History

- `docs/current-state.json` — canonical typed active state and repository-local
  evidence references.
- `docs/architecture/school-learning.md` — durable published School Learning
  contract.
- `docs/reviews/clean-foundation-f1-acceptance-and-publication-2026-07-31.md`
  — dated F1 acceptance and bounded publication-authority evidence.
- `docs/reviews/school-learning-v0-1-pilot-evaluation-2026-07-21.md` — dated
  pilot, acceptance, and publication evidence.
- `docs/docs-map.md` — navigation to architecture, dated reviews, roadmaps, and
  historical infrastructure records.
- Git history — complete implementation, correction, acceptance, and
  publication history.

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

- docs/current-state.json
- docs/current-mission.md
- docs/architecture/repository.md
- docs/architecture/atlas.md
- docs/infrastructure.md
- docs/infrastructure-gamer-pve.md
- docs/services.md
- Git history

## Use Boundary

- Canonical repository sources win over this generated view.
- Live branch, worktree, infrastructure, and external-system state require fresh observation.
- Task, implementation, publication, deployment, and external-write authority require explicit owner instruction outside repository state.
- Never include secrets or personal School Learning data.
