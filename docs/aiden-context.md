# Aiden Context

Generated: 2026-08-01

## Purpose

This file is an AI-readable context packet for the Aiden Platform engineering repository.

It projects canonical active state, its human companion, and the existing infrastructure summary. It is generated and non-canonical.

## Canonical Active State

- Schema version: 1
- Effective date: 2026-08-01
- Phase: Clean Foundation F1 — Canonical State, Authority, and Orientation — Published
- Phase lifecycle: published
- Work selection: selected
- Selected checkpoint: W1 — Engineering Workflow v1.1
- Intentional idle: No
- Decision required: `review-w1-implementation-candidate` — Obtain a fresh adversarial independent review of the local W1 implementation candidate before owner acceptance.

### Blockers

- None

### Unknowns

- None

### Evidence

- `clean-foundation-f1-publication`: `docs/reviews/clean-foundation-f1-acceptance-and-publication-2026-07-31.md` at `7339e1676f7588e319e3cb004d56baf56a37bed6` (records_phase)

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

Clean Foundation F1 — Canonical State, Authority, and Orientation — Published

### Active State

Clean Foundation F1 remains accepted and published. W1 — Engineering Workflow
v1.1 remains selected and has a verified uncommitted local implementation
candidate awaiting fresh adversarial independent review. Selection and local
verification do not make W1 implementation-complete, accepted, published, or
operational.

Canonical state effective date: 2026-08-01.

### Mission Intent

Preserve the bounded W1 local candidate, its compact evidence, unchanged Atlas
behavior, and isolated readiness fixtures while awaiting the required fresh
adversarial independent review.

### Work Selection

- Status: Selected.
- Selected checkpoint: W1 — Engineering Workflow v1.1.
- W1 lifecycle: Selected; verified uncommitted local candidate awaiting fresh
  adversarial independent review.
- R1, S1, F2, F3, and all other future checkpoints: Not selected.

### Next Milestone

W1 — Engineering Workflow v1.1

### Blockers

None recorded in canonical active state.

### Unknowns

None recorded in canonical active state.

### Owner Decision Required

Obtain a fresh adversarial independent review of the local W1 implementation
candidate before owner acceptance.

### Authority Boundary

Repository state selects work but grants no task, implementation, publication,
deployment, or external-write authority. Atlas observes and explains state but
grants no authority. Task, implementation, and publication authority remain
external and not established by repository state or Atlas. `AGENTS.md` is the
primary repository-local authority-interpretation contract.

### Evidence and History

- `docs/current-state.json` — canonical typed active state and repository-local
  evidence references.
- `docs/reviews/clean-foundation-f1-acceptance-and-publication-2026-07-31.md`
  at `7339e1676f7588e319e3cb004d56baf56a37bed6` — accepted F1 implementation
  and publication evidence.
- `docs/reviews/engineering-workflow-v1-1-evidence-2026-08-01.md` — compact W1
  checkpoint brief and verified local implementation evidence; no immutable
  candidate identity exists before a separately authorized commit.
- Git history — immutable implementation and publication identities.

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
