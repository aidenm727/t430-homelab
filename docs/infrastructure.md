# Public-Safe Infrastructure Record

**Evidence window:** 2026-06-23 through 2026-06-24
**Continuity claim:** None; current reality requires fresh authorized observation

## Purpose

This document is the canonical public owner for infrastructure roles, trust
boundaries, operating patterns, and sanitized dated evidence. It deliberately
does not contain addresses, real host or private DNS identities, exact inventory,
endpoints, ports, container IDs, device or storage paths, management paths,
backup destinations, credential references, or executable recovery steps.

Exact operational facts belong in a future private operations repository only
when a real artifact requires version control. Secret values belong only in a
secret manager or protected operational storage and never in Git.

## Role Topology

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

## Capability Classes

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

## Trust Boundaries

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

## Dated Operational Evidence

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

## Backup and Recovery Pattern

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

## Operations and Change Discipline

Repository change records preserve what was attempted, why, the date, and a
public-safe verification outcome. Live operations require separate authority
and fresh evidence. A change should progress from experiment to supported
capability only after its ownership, data boundary, observation, backup,
rollback, and recovery expectations are understandable.

## Known Limits

- The dated restore evidence is not a current recovery guarantee.
- Exact live inventory is intentionally absent from this public repository.
- The virtualization environment's primary storage is not an independent
  failure domain.
- Local-AI operation and a dedicated storage environment remain future work.
- A private operations repository remains conditional on an exact artifact
  needing durable restricted ownership.

## Canonical Links

- [Virtualization record](infrastructure-virtualization.md)
- [Service capability record](services.md)
- [Compute architecture](architecture/compute.md)
- [Repository public/private boundary](architecture/repository.md)
- [Dated generalized change records](changes/)
