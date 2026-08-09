# Aiden Context

Generated: 2026-08-08 (canonical-state effective date; deterministic)

## Purpose

This file is an AI-readable generated context packet for the public Aiden
Platform engineering repository. It projects canonical active state, its human
companion, and the registered public-safe infrastructure snapshot. It is
generated and non-canonical.

## Canonical Active State

- Schema version: 1
- Effective date: 2026-08-08
- Phase: W1 — Engineering Workflow v1.1 — Published
- Phase lifecycle: published
- Work selection: intentional_idle
- Selected checkpoint: None
- Intentional idle: Yes
- Decision required: `select-future-work` — Owner selection of future work; no checkpoint or later capability is preselected.

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
active selected work. R1 — Repository Identity and Public/Private Boundary is
owner-accepted, published, and complete. G14 Storage Orientation Snapshot is
owner-accepted, published, and complete. No implementation checkpoint is
selected, and repository work selection is intentionally idle. G14 completion
does not claim live collection, deployment, or an operational runtime state.

Canonical state effective date: 2026-08-08.

### Mission Intent

Preserve the published Workflow v1.1, completed R1, and completed metadata-only
G14 storage-orientation foundation, human authority, generated ownership, and
all public/private boundaries while the owner chooses future work. No live
collection, deployment, or operational-runtime claim is established.

### Work Selection

- Status: Intentional idle.
- Selected checkpoint: None.
- G14 lifecycle: Owner-accepted, published, and complete; not active selected
  work. Deployment, live collection, and operational runtime are not claimed.
- W1 lifecycle: Published and complete; not active selected work.
- R1 lifecycle: Owner-accepted, published, and complete; not active selected
  work.
- S1, F2, F3, and all other future checkpoints: Not selected.

### Next Milestone

Intentional idle — no engineering checkpoint is selected.

### Blockers

None recorded in canonical active state.

### Unknowns

None recorded in canonical active state.

### Owner Decision Required

Owner selection of future work. No checkpoint, capability, S1, F2, F3, or other
follow-on work is preselected.

### Authority Boundary

Repository state selects work but grants no task, implementation, publication,
deployment, or external-write authority. Atlas observes and explains state but
grants no authority. Any task, implementation, staging, commit, ref or remote
mutation, publication, deployment, GitHub action, or other external write
requires explicit owner authority outside repository state and Atlas.
`AGENTS.md` is the primary repository-local authority-interpretation contract.

### Evidence and History

- `docs/current-state.json` — canonical typed active state and repository-local
  evidence references.
- `docs/reviews/engineering-workflow-v1-1-evidence-2026-08-01.md` — compact W1
  checkpoint, acceptance, and publication evidence at the accepted candidate
  commit `27d99c1eb0ab30f7fcd11158f4c1d856bd6913de`.
- `docs/reviews/clean-foundation-f1-acceptance-and-publication-2026-07-31.md`
  at `7339e1676f7588e319e3cb004d56baf56a37bed6` — historical accepted and
  published F1 foundation evidence.
- `docs/reviews/repository-identity-r1-evidence-2026-08-02.md` — compact R1
  chronology through owner acceptance, first publication, the verified rename,
  post-rename identity finalization, and the published-and-complete lifecycle
  transition.
- `docs/reviews/g14-storage-orientation-snapshot-implementation-evidence-2026-08-08.md`
  — compact Tier 3 G14 implementation, review, acceptance, verification,
  residual-limitation, and publication-boundary evidence.
- Git history — immutable implementation and publication identities.

## Infrastructure Snapshot

> Generated public context artifact.
> Do not edit directly; update the registered canonical infrastructure sources.

This snapshot contains role-based patterns and dated, non-continuous evidence.
It contains no live-state guarantee or exact private operations record.

### Infrastructure

Source: `docs/infrastructure.md`

**Evidence window:** 2026-06-23 through 2026-06-24
**Continuity claim:** None; current reality requires fresh authorized observation

#### Purpose

This document is the canonical public owner for infrastructure roles, trust
boundaries, operating patterns, and sanitized dated evidence. It deliberately
does not contain addresses, real host or private DNS identities, exact inventory,
endpoints, ports, container IDs, device or storage paths, management paths,
backup destinations, credential references, or executable recovery steps.

Exact operational facts belong in a future private operations repository only
when a real artifact requires version control. Secret values belong only in a
secret manager or protected operational storage and never in Git.

#### Role Topology

```text
Owner devices
    │
    ├── private access boundary
    │
    ▼
Core-services environment
    ├── network and name-resolution capabilities
    ├── ingress and certificate boundary
    ├── observability capabilities
    ├── selected owner services
    └── backup coordination
             │
             ├── encrypted off-host/off-site protection pattern
             │
             └── bounded restore evidence

Virtualization environment
    ├── isolated VM/LXC workloads
    ├── application experiments
    └── migration and future compute capacity
```

Role aliases describe architectural responsibility, not reachable systems.

#### Capability Classes

| Class | Public pattern | Representative technology |
| --- | --- | --- |
| Private access | Administrative paths are restricted to owner-controlled private access | Tailscale-class overlay access |
| Network services | Local name resolution and policy remain separate from public ingress | Pi-hole-class DNS filtering |
| Ingress | One reverse-proxy boundary terminates internal HTTPS and routes approved services | Traefik-class reverse proxy |
| Observability | Metrics, logs, health checks, dashboards, and alerts are separate capabilities | Prometheus/Grafana/Loki-class stack |
| Owner services | Selected personal services run behind the same trust and evidence boundaries | Password-management and media-workflow classes |
| Backup and recovery | Local snapshots, encrypted independent copies, verification, and bounded restore tests are distinct controls | Content-addressed backup tooling |

Representative technologies explain engineering choices; the table is not a
complete live inventory or route list.

#### Trust Boundaries

- The human owner remains the authority for goals, access, changes, acceptance,
  and recovery decisions.
- Public documentation cannot establish current reachability or health.
- Private access reduces exposure but does not replace service authentication,
  patching, least privilege, or backup.
- Ingress, observability, application data, and backup each have distinct data
  and failure boundaries.
- Generated repository context is a public release and derives only from this
  sanitized record, the virtualization record, and the service-capability
  record.

#### Dated Operational Evidence

The June 2026 source records documented the following bounded outcomes:

- a resource-constrained core-services environment recovered its containerized
  workloads after a planned restart and received explicit service checks;
- local DNS, private access, internal HTTPS, metrics, logs, dashboards, health
  checks, and alert delivery were individually verified;
- backup snapshots could be listed, a bounded full restore was completed, and a
  later encrypted off-site retrieval was verified;
- a separate virtualization environment received local workload capacity,
  private remote administration, node monitoring, and an initial application
  workload.

These are historical observations from 2026-06-23 and 2026-06-24. They do not
prove that any system is currently online, reachable, protected, or restorable.

#### Backup and Recovery Pattern

```text
Application-owned data
    ├── portable export when supported
    ├── local versioned snapshot
    ├── encrypted off-host copy
    └── encrypted off-site copy
             │
             └── dated integrity and restore evidence
```

Primary capacity, snapshots, independent backup, off-site protection, and
restore proof are different controls. Public evidence may record objectives,
method class, date, and redacted outcome. Provider identity, repository or
bucket names, key and configuration locations, exact commands, and destinations
remain private.

#### Operations and Change Discipline

Repository change records preserve what was attempted, why, the date, and a
public-safe verification outcome. Live operations require separate authority
and fresh evidence. A change should progress from experiment to supported
capability only after its ownership, data boundary, observation, backup,
rollback, and recovery expectations are understandable.

#### Known Limits

- The dated restore evidence is not a current recovery guarantee.
- Exact live inventory is intentionally absent from this public repository.
- The virtualization environment's primary storage is not an independent
  failure domain.
- Local-AI operation and a dedicated storage environment remain future work.
- A private operations repository remains conditional on an exact artifact
  needing durable restricted ownership.

#### Canonical Links

- [Virtualization record](infrastructure-virtualization.md)
- [Service capability record](services.md)
- [Compute architecture](architecture/compute.md)
- [Repository public/private boundary](architecture/repository.md)
- [Dated generalized change records](changes/)

### Infrastructure Virtualization

Source: `docs/infrastructure-virtualization.md`

**Evidence window:** 2026-06-23 through 2026-06-24
**Continuity claim:** None; current reality requires fresh authorized observation

#### Purpose

This document preserves the engineering value of the platform's virtualization
history without publishing a real host identity, address, private DNS, exact
hardware inventory, endpoint, port, guest ID, device or storage path, or
management procedure.

#### Role

The virtualization environment is the flexible compute boundary for isolated
VM and LXC workloads, application experiments, migration work, and potential
future resource-intensive capability. It is distinct from the lower-change
core-services environment.

The documented implementation used Proxmox VE on repurposed workstation-class
hardware. That technology choice is historical and representative; no current
version, health, capacity, or availability is claimed.

#### Storage and Failure Boundaries

The June 23 change record documents that existing local solid-state capacity
was reassigned into a workload-oriented virtualization pool only after an
existing archive copy was checked on separate media. The public record retains
that preservation decision while omitting device, volume, pool, size, vendor,
mount, and archive-location identities.

Local workload capacity improves placement and rollback options but remains in
the virtualization host's failure domain. It is not an independent backup or a
demonstrated migration target.

#### Dated Workload Evidence

On 2026-06-24, the records documented:

- a Debian-class system container used as an isolated application boundary;
- an Immich media-workflow stack deployed with Docker Compose as the first
  application workload on the new pool;
- application and component health checks returning expected results;
- node metrics added to the existing observability model; and
- private overlay administration verified without making management public.

This is sanitized historical evidence. It is not a complete workload inventory,
proof of present operation, proof of protected data, or proof of recoverability.

#### Migration Reasoning

- Keep application data ownership explicit and prefer portable exports.
- Separate guest configuration, application state, attachments, and backup
  ownership.
- Treat hypervisor-local snapshots as rollback, not independent protection.
- Verify restore on a clean target before describing a workload as dependable.
- Avoid making a service depend on the original host identity, storage device,
  private route, or hypervisor-specific path.
- Record exact deployment and recovery artifacts privately only when they need
  durable version control.

#### Future Compute

A reversible local-AI experiment may later use this role, but no GPU identity,
driver readiness, passthrough, model fit, privacy behavior, benchmark, or
operational result is claimed here. Knowledge and School Learning workflows
must remain functional without local inference.

#### Public Boundary

The public record owns role separation, representative technology, dated
outcomes, storage/recovery reasoning, and migration principles. Exact inventory,
addressing, private DNS, guests, configuration, backup destinations, recovery
steps, incidents, and live evidence belong to future private operations
ownership if and when such artifacts exist.

See [the platform infrastructure record](infrastructure.md), [service
capabilities](services.md), and [compute architecture](architecture/compute.md).

### Services

Source: `docs/services.md`

**Evidence window:** 2026-06-23 through 2026-06-24
**Continuity claim:** None; this is not a live service catalog

#### Purpose

This record describes service capability classes, trust boundaries,
representative technologies, and dated verification without publishing a
complete inventory, endpoint, route, port, container identity, data or config
path, private DNS name, or management procedure.

#### Capability Matrix

| Capability | Engineering role | Representative technology | Dated public evidence |
| --- | --- | --- | --- |
| Owner start page and health view | Gives the owner a concise operational entry point without becoming the source of truth | Homepage- and Uptime-Kuma-class tools | Page rendering and health-check behavior were verified in the June 2026 record |
| Metrics and dashboards | Separates measurement, storage, presentation, and alerting | Prometheus- and Grafana-class tools | Host and virtualization-node metrics plus dashboard queries were checked on 2026-06-24 |
| Central logs | Supports bounded diagnosis without treating logs as canonical state | Loki- and Alloy-class tools | Log ingestion and query behavior were recorded as verified in June 2026 |
| Local network policy | Provides owner-controlled name resolution and filtering | Pi-hole-class DNS tooling | Local resolution behavior was checked during the evidence window |
| Private ingress | Routes explicitly approved internal services behind an HTTPS boundary | Traefik-class proxy and private overlay access | Private routing and certificate behavior were checked during the evidence window |
| Owner data service | Demonstrates an isolated application workflow | Immich with Docker Compose | Initial component health and application response were checked on 2026-06-24 |
| Encrypted backup | Separates backup creation, independent copies, verification, and restore | Content-addressed encrypted backup tooling | Snapshot listing, bounded restore, and later off-site retrieval were recorded as successful |

The technology names are representative examples from dated records. This
matrix is intentionally not an exhaustive current inventory.

#### Service Boundaries

- Public documentation describes why a capability exists and how trust is
  separated; it does not describe how to reach or administer it.
- Service authentication remains independent from private network access.
- Dashboards and alerts are observations, not authoritative proof of state.
- Application data, configuration, logs, and backup each have separate
  retention and recovery concerns.
- Secret values and credential references never belong in Git.
- Current health, version, exposure, and inventory require fresh authorized
  observation.

#### Evidence Interpretation

The historical records show that the owner built and checked a small network,
observability, ingress, application, and recovery stack under constrained
hardware. They do not establish continuous availability, production scale,
production-grade model serving, current patch level, or current recovery time.

Executable runbooks, exact destinations, inventory, incident records, and
private live evidence are candidates for a future private operations repository
only when durable restricted version control becomes necessary.

See [the public infrastructure owner](infrastructure.md) and [virtualization
record](infrastructure-virtualization.md).

## Recent Changes

- 2026-06-26 — Prototype Aiden engineering toolkit
- 2026-06-24 — Refine infrastructure documentation structure
- 2026-06-24 — Improve recent changes ordering
- 2026-06-24 — Improve generated AI context formatting
- 2026-06-24 — Generate infrastructure snapshot from context tool

## Registered Source Graph

- docs/current-state.json
- docs/current-mission.md
- docs/infrastructure-snapshot.md
- docs/changes/ (`*.yml` structured records)

The generated infrastructure snapshot declares its canonical infrastructure
sources. Git history records repository evolution but is not a generator input.

## Use Boundary

- Canonical repository sources win over this generated view.
- Live branch, worktree, infrastructure, and external-system state require fresh observation.
- Task, implementation, publication, deployment, and external-write authority require explicit owner instruction outside repository state.
- Exact private operations, secrets, credentials, and personal School Learning data are excluded.
