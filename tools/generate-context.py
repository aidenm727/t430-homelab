from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

output = f"""# Aiden Context

Generated: {date.today().isoformat()}

## Purpose

This file is an AI-readable context packet for the homelab project.

It summarizes the current state, active priorities, and operating rules so an AI assistant can quickly understand where the project stands.

## Current Mission

Platform Expansion & AI Workflow Foundation

## Current Focus

- Learn and establish Proxmox virtualization workflows
- Expand homelab capacity beyond the T430
- Build AI-assisted documentation and context workflows
- Build foundations for Aiden OS

## Infrastructure Snapshot

### Production Host

t430-beast

- Role: Production services host
- OS: Ubuntu Server 24.04 LTS
- LAN IP: 10.0.0.136
- Responsibilities:
  - Pi-hole
  - Traefik
  - Grafana
  - Prometheus
  - Loki
  - Alloy
  - Uptime Kuma
  - Vaultwarden
  - Backup infrastructure

### Virtualization Host

gamer-pve

- Role: Proxmox virtualization host
- OS: Proxmox VE 9.2
- LAN IP: 10.0.0.178
- Hardware:
  - Ryzen 5 2600
  - 16 GB DDR4
  - RTX 4060-class GPU
- Storage:
  - 500 GB WDC SSD: Proxmox OS
  - 1 TB SPCC NVMe SSD: preserved storage
  - 2 TB WD Blue SA510 SSD: preserved storage
- Purpose:
  - VM hosting
  - Container hosting
  - Future Immich deployment
  - Future AI workloads

## Active Services

- Pi-hole
- Traefik
- Homepage
- Uptime Kuma
- Grafana
- Prometheus
- Loki
- Alloy
- Vaultwarden

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

## Next Milestone

Deploy the first VM on gamer-pve and document the VM architecture using the new documentation workflow.
"""

(DOCS / "aiden-context.md").write_text(output, encoding="utf-8")
print("Generated docs/aiden-context.md")