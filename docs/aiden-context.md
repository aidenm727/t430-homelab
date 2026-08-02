# Aiden Context

Generated: 2026-08-02

## Purpose

This file is an AI-readable context packet for the Aiden Platform engineering repository.

It projects canonical active state, its human companion, and the existing infrastructure summary. It is generated and non-canonical.

## Canonical Active State

- Schema version: 1
- Effective date: 2026-08-01
- Phase: W1 — Engineering Workflow v1.1 — Published
- Phase lifecycle: published
- Work selection: intentional_idle
- Selected checkpoint: None
- Intentional idle: Yes
- Decision required: `select-future-engineering-checkpoint` — Owner selection of a future engineering checkpoint or continued intentional idle; R1 remains a proposed option and is not selected.

### Blockers

- None

### Unknowns

- None

### Evidence

- `engineering-workflow-v1-1-publication`: `docs/reviews/engineering-workflow-v1-1-evidence-2026-08-01.md` at `27d99c1eb0ab30f7fcd11158f4c1d856bd6913de` (records_phase)

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

W1 — Engineering Workflow v1.1 — Published

### Active State

W1 — Engineering Workflow v1.1 is owner-accepted, published, and complete. Clean
Foundation F1 remains historical published foundation evidence rather than
active selected work. No follow-on checkpoint is selected or authorized.

Canonical state effective date: 2026-08-01.

### Mission Intent

Preserve the published Workflow v1.1 contract, unchanged Atlas behavior,
isolated readiness fixtures, compact W1 evidence, and the historical F1
foundation while remaining intentionally idle pending an explicit owner
decision.

### Work Selection

- Status: Intentional idle.
- Selected checkpoint: None.
- W1 lifecycle: Published and complete; not active selected work.
- R1, S1, F2, F3, and all other future checkpoints: Not selected.

### Next Milestone

Intentional idle — no engineering checkpoint is selected.

### Blockers

None recorded in canonical active state.

### Unknowns

None recorded in canonical active state.

### Owner Decision Required

Select a future engineering checkpoint or continue intentional idle. R1 remains
a proposed option only; it is not selected or authorized.

### Authority Boundary

Repository state selects work but grants no task, implementation, publication,
deployment, or external-write authority. Atlas observes and explains state but
grants no authority. No follow-on task, implementation, publication,
deployment, or external-write authority is established by W1 completion,
repository state, or Atlas. `AGENTS.md` is the primary repository-local
authority-interpretation contract.

### Evidence and History

- `docs/current-state.json` — canonical typed active state and repository-local
  evidence references.
- `docs/reviews/engineering-workflow-v1-1-evidence-2026-08-01.md` — compact W1
  checkpoint, acceptance, and publication evidence at the accepted candidate
  commit `27d99c1eb0ab30f7fcd11158f4c1d856bd6913de`.
- `docs/reviews/clean-foundation-f1-acceptance-and-publication-2026-07-31.md`
  at `7339e1676f7588e319e3cb004d56baf56a37bed6` — historical accepted and
  published F1 foundation evidence.
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
