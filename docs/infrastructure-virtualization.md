# Public-Safe Virtualization Infrastructure Record

**Evidence window:** 2026-06-23 through 2026-06-24
**Continuity claim:** None; current reality requires fresh authorized observation

## Purpose

This document preserves the engineering value of the platform's virtualization
history without publishing a real host identity, address, private DNS, exact
hardware inventory, endpoint, port, guest ID, device or storage path, or
management procedure.

## Role

The virtualization environment is the flexible compute boundary for isolated
VM and LXC workloads, application experiments, migration work, and potential
future resource-intensive capability. It is distinct from the lower-change
core-services environment.

The documented implementation used Proxmox VE on repurposed workstation-class
hardware. That technology choice is historical and representative; no current
version, health, capacity, or availability is claimed.

## Storage and Failure Boundaries

The June 23 change record documents that existing local solid-state capacity
was reassigned into a workload-oriented virtualization pool only after an
existing archive copy was checked on separate media. The public record retains
that preservation decision while omitting device, volume, pool, size, vendor,
mount, and archive-location identities.

Local workload capacity improves placement and rollback options but remains in
the virtualization host's failure domain. It is not an independent backup or a
demonstrated migration target.

## Dated Workload Evidence

On 2026-06-24, the records documented:

- a Debian-class system container used as an isolated application boundary;
- an Immich media-workflow stack deployed with Docker Compose as the first
  application workload on the new pool;
- application and component health checks returning expected results;
- node metrics added to the existing observability model; and
- private overlay administration verified without making management public.

This is sanitized historical evidence. It is not a complete workload inventory,
proof of present operation, proof of protected data, or proof of recoverability.

## Migration Reasoning

- Keep application data ownership explicit and prefer portable exports.
- Separate guest configuration, application state, attachments, and backup
  ownership.
- Treat hypervisor-local snapshots as rollback, not independent protection.
- Verify restore on a clean target before describing a workload as dependable.
- Avoid making a service depend on the original host identity, storage device,
  private route, or hypervisor-specific path.
- Record exact deployment and recovery artifacts privately only when they need
  durable version control.

## Future Compute

A reversible local-AI experiment may later use this role, but no GPU identity,
driver readiness, passthrough, model fit, privacy behavior, benchmark, or
operational result is claimed here. Knowledge and School Learning workflows
must remain functional without local inference.

## Public Boundary

The public record owns role separation, representative technology, dated
outcomes, storage/recovery reasoning, and migration principles. Exact inventory,
addressing, private DNS, guests, configuration, backup destinations, recovery
steps, incidents, and live evidence belong to future private operations
ownership if and when such artifacts exist.

See [the platform infrastructure record](infrastructure.md), [service
capabilities](services.md), and [compute architecture](architecture/compute.md).
