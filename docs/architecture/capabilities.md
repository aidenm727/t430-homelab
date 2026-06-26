# Platform Capability Map

## Purpose

This document defines the major capabilities of the Aiden Platform.

A capability is something the platform should be able to do, independent of the specific service, tool, or hardware used to implement it.

The goal is to plan the platform by asking:

> What capability are we improving?

Rather than:

> What service should we install next?

## Core Principle

The Aiden Platform evolves by strengthening capabilities over time.

Services, servers, containers, VMs, scripts, and AI tools are implementation details.

Capabilities are the long-term structure.

## Capability Areas

## 1. Compute

The platform should provide reliable places to run workloads.

Includes:

* Docker workloads
* LXC containers
* Virtual machines
* GPU workloads
* Experimental compute environments

Current implementations:

* t430-beast
* gamer-pve
* Docker Compose
* Proxmox

## 2. Storage

The platform should safely store, organize, protect, and retrieve data.

Includes:

* Service data
* Backups
* Photos
* Documents
* Archives
* Media
* Future NAS storage

Current implementations:

* t430-beast local SSD
* gamer-pve SSD storage
* Restic backups
* Backblaze B2 off-site backup
* Preservation archive

## 3. Networking and Access

The platform should provide secure, reliable access to services.

Includes:

* Internal DNS
* Reverse proxy routing
* HTTPS
* VPN access
* Access control

Current implementations:

* Pi-hole
* Traefik
* Tailscale
* Internal PKI
* home.lab DNS

## 4. Observability

The platform should make health, performance, logs, and failures visible.

Includes:

* Metrics
* Logs
* Dashboards
* Uptime monitoring
* Alerts
* Health checks

Current implementations:

* Grafana
* Prometheus
* Loki
* Alloy
* Uptime Kuma
* Discord alerts

## 5. Automation

The platform should reduce manual work and make operations repeatable.

Includes:

* Configuration management
* Health-check playbooks
* Backup automation
* Context generation
* Future deployment automation

Current implementations:

* Ansible
* systemd timers
* generate-context.py
* homelab-change.py

## 6. Knowledge and Documentation

The platform should explain itself to both humans and AI assistants.

Includes:

* Infrastructure records
* Architecture documents
* Change logs
* Generated AI context
* Future searchable knowledge base

Current implementations:

* docs/infrastructure.md
* docs/infrastructure-gamer-pve.md
* docs/services.md
* docs/architecture/platform.md
* docs/architecture/engineering.md
* docs/aiden-context.md
* docs/current-mission.md
* docs/infrastructure-snapshot.md
* docs/changes.log

## 7. Engineering

The platform should provide repeatable ways to design, inspect, validate, document, and evolve itself.

Includes:

* Engineering state inspection
* Change workflow support
* Repository validation
* Documentation validation
* Architecture awareness
* AI context preparation
* Future unified engineering CLI

Current implementations:

* Atlas
* generate-context.py
* homelab-change.py
* aiden-context-loader.py
* Structured change workflow

## 8. Personal Services

The platform should provide useful personal digital services.

Includes:

* Password management
* Photo management
* Document management
* Media access
* Dashboards
* Future personal cloud services

Current implementations:

* Vaultwarden
* Homepage
* Immich

## 9. AI and Aiden OS

The platform should eventually support AI-native workflows.

Includes:

* Local AI models
* AI-assisted documentation
* Personal tutors
* Daily briefings
* Search and retrieval
* Memory/context systems
* Future Aiden OS components

Current implementations:

* ChatGPT Project workflow
* AI-readable context files
* Context generation scripts
* Architecture-first planning

## Capability Maturity

Each capability can exist at different levels of maturity.

### Level 0 — Not Started

The capability is only an idea.

### Level 1 — Experimental

The capability is being explored, tested, or prototyped.

### Level 2 — Operational

The capability works and is useful, but may not be fully automated, monitored, or documented.

### Level 3 — Production

The capability is reliable, documented, monitored, backed up where appropriate, and integrated into normal operations.

### Level 4 — Platform Native

The capability is deeply integrated into the platform and improves other capabilities.

## Current Capability Assessment

| Capability                  | Current Maturity | Notes                                                                       |
| --------------------------- | ---------------: | --------------------------------------------------------------------------- |
| Compute                     |          Level 2 | Docker and Proxmox are operational, but VM workflow is still maturing.      |
| Storage                     |          Level 2 | Backups are strong, but long-term NAS/storage architecture is not complete. |
| Networking and Access       |          Level 3 | DNS, HTTPS, Tailscale, and reverse proxy are established.                   |
| Observability               |          Level 3 | Metrics, logs, alerts, and health checks exist for core services.           |
| Automation                  |          Level 2 | Ansible and scripts exist, but deployment automation is still early.        |
| Knowledge and Documentation |          Level 3 | Documentation system is becoming a core platform strength.                  |
| Engineering                 |          Level 1 | Atlas architecture has been defined; initial toolkit implementation is beginning. 
| Personal Services           |          Level 2 | Several useful services exist, but the service layer is still growing.      |
| AI and Aiden OS             |          Level 1 | Strong concept and workflow foundation, but local implementation is early.  |


## Planning Rule

Future work should be selected by identifying the weakest or highest-value capability, then choosing an implementation that improves it.

A service should not be added only because it is interesting.

A service should be added because it improves a defined platform capability.

## Next Capability Priorities

1. Engineering toolkit / Atlas
2. Storage architecture
3. Compute architecture
4. AI/context architecture
5. Proxmox VM workflow
