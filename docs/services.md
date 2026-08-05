# Public-Safe Service Capability Record

**Evidence window:** 2026-06-23 through 2026-06-24
**Continuity claim:** None; this is not a live service catalog

## Purpose

This record describes service capability classes, trust boundaries,
representative technologies, and dated verification without publishing a
complete inventory, endpoint, route, port, container identity, data or config
path, private DNS name, or management procedure.

## Capability Matrix

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

## Service Boundaries

- Public documentation describes why a capability exists and how trust is
  separated; it does not describe how to reach or administer it.
- Service authentication remains independent from private network access.
- Dashboards and alerts are observations, not authoritative proof of state.
- Application data, configuration, logs, and backup each have separate
  retention and recovery concerns.
- Secret values and credential references never belong in Git.
- Current health, version, exposure, and inventory require fresh authorized
  observation.

## Evidence Interpretation

The historical records show that the owner built and checked a small network,
observability, ingress, application, and recovery stack under constrained
hardware. They do not establish continuous availability, production scale,
production-grade model serving, current patch level, or current recovery time.

Executable runbooks, exact destinations, inventory, incident records, and
private live evidence are candidates for a future private operations repository
only when durable restricted version control becomes necessary.

See [the public infrastructure owner](infrastructure.md) and [virtualization
record](infrastructure-virtualization.md).
