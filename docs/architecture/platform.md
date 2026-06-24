# Platform Architecture

## Purpose

The Aiden Platform exists to make the bridge between physical life and digital life powerful, private, personal, and simple.

It should become the primary home for the owner's digital life: services, photos, media, projects, documents, knowledge, automation, and AI-assisted workflows.

The platform should feel easy to use, clean, personalized, and exciting to return to.

## Design Vision

The platform is not just a collection of self-hosted services.

It is intended to become a personal operating environment: a home OS that makes digital life easier to access, understand, customize, and control.

AI should eventually abstract complexity where appropriate while preserving transparency and user control.

## Core Principles

### Data Ownership

Important personal data should remain under the owner's control whenever practical.

The platform should reduce dependence on external cloud services without rejecting them unnecessarily.

### Privacy

Services should be private by default.

Remote access should use secure private networking rather than public exposure unless there is a clear reason to do otherwise.

### Simplicity

The platform should be easy to use and easy to understand.

Complexity is acceptable behind the scenes only when it creates meaningful reliability, security, or capability.

### Personalization

The platform should reflect the owner's workflows, interests, projects, and life.

It should become more useful as it learns the owner's systems and preferences.

### Data Outlives Compute

Servers, virtual machines, containers, and applications are replaceable.

Personal data, photos, documents, archives, project history, and knowledge should survive hardware changes.

### Capability-Driven Growth

New services should be added because they provide a meaningful platform capability, not simply because they are interesting to install.

## Platform Capabilities

Current and planned capabilities include:

- Networking and secure access
- Internal DNS
- Reverse proxy and HTTPS
- Monitoring and observability
- Backups and restore validation
- Virtualization
- Documentation and operational history
- AI-readable context generation
- Long-term storage
- Personal cloud services
- Local AI and automation
- AidenOS orchestration

## Current Implementation

### t430-beast

Primary stable infrastructure host.

Responsibilities include:

- DNS
- Reverse proxy
- Monitoring
- Core Docker services
- Backup infrastructure
- Operational tooling

### gamer-pve

Proxmox compute and virtualization host.

Responsibilities include:

- VMs
- LXC containers
- Immich
- Future AI workloads
- Resource-intensive services

### Future NAS

Planned dedicated storage layer.

Responsibilities may include:

- Photos and videos
- Documents
- Media
- Archives
- Preservation migration target
- VM and LXC backups
- Shared storage
- Off-site backup source

## Long-Term Direction

The long-term direction is to evolve from a homelab into a personal digital infrastructure platform.

The platform should support:

- replacing selected cloud services,
- preserving important personal data,
- improving daily workflows,
- supporting AI-assisted learning and automation,
- and eventually forming the foundation for AidenOS.

## Build Philosophy

Prefer deliberate capability growth over reactive service installation.

The standard project loop should be:

1. Learn
2. Design
3. Implement
4. Verify
5. Document

Infrastructure should remain understandable, recoverable, and intentionally designed.