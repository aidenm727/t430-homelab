from pathlib import Path
from datetime import date
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

def prepare_embedded_markdown(text):
    lines = text.splitlines()

    if lines and lines[0].startswith("# "):
        lines = lines[1:]

    prepared = []

    for line in lines:
        if line.startswith("### "):
            prepared.append("#" + line)
        elif line.startswith("## "):
            prepared.append("#" + line)
        else:
            prepared.append(line)

    return "\n".join(prepared).strip()

def build_infrastructure_snapshot():
    return """# Infrastructure Snapshot

> Generated context artifact.
> Do not edit directly; update canonical infrastructure records instead.

## Production Host

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

## Virtualization Host

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

## Active Workloads

### LXC 200 - Immich

* Debian 12
* Docker Engine
* Docker Compose
* 128 GB root disk
* LAN IP: 10.0.0.132

## Active Services

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
"""

def load_recent_changes(limit=5):
    changes_dir = DOCS / "changes"

    if not changes_dir.exists():
        return ["No structured change records found."]

    changes = []

    for path in sorted(changes_dir.glob("*.yml"), key=lambda p: p.stat().st_mtime, reverse=True):
        text = path.read_text(encoding="utf-8")

        title_match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        date_match = re.search(r"^date:\s*(.+)$", text, re.MULTILINE)

        if title_match and date_match:
            changes.append(
                f"- {date_match.group(1)} — {title_match.group(1)}"
            )

    return changes[:limit]

change_session_path = DOCS / "change-session.md"

if change_session_path.exists():
    change_session = change_session_path.read_text(encoding="utf-8")
else:
    change_session = "No active change session found."

mission_path = DOCS / "current-mission.md"

if mission_path.exists():
    mission = prepare_embedded_markdown(mission_path.read_text(encoding="utf-8"))
else:
    mission = "Mission document missing."

snapshot_path = DOCS / "infrastructure-snapshot.md"
snapshot_path.write_text(build_infrastructure_snapshot(), encoding="utf-8")
snapshot = prepare_embedded_markdown(snapshot_path.read_text(encoding="utf-8"))
recent_changes = "\n".join(load_recent_changes())

output = f"""# Aiden Context

Generated: {date.today().isoformat()}

## Purpose

This file is an AI-readable context packet for the homelab project.

It summarizes the current state, active priorities, and operating rules so an AI assistant can quickly understand where the project stands.

## Current Mission

{mission}

## Infrastructure Snapshot

{snapshot}

## Recent Changes

{recent_changes}

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

## Active Change Session

{change_session}

## Next Milestone

Deploy the first VM on gamer-pve and document the VM architecture using the new documentation workflow.
"""

(DOCS / "aiden-context.md").write_text(output, encoding="utf-8")
print("Generated docs/aiden-context.md")