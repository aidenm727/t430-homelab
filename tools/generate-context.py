from pathlib import Path
from datetime import date
import re

from atlas.platform.active_state import load_active_state
from atlas.platform.reasoning.synchronization import (
    render_generated_context_active_state,
)


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


active_state = load_active_state(repository_root=ROOT)
active_state_projection = render_generated_context_active_state(active_state)

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

This file is an AI-readable context packet for the Aiden Platform engineering repository.

It projects canonical active state, its human companion, and the existing infrastructure summary. It is generated and non-canonical.

{active_state_projection}

## Current Mission Companion

{mission}

## Infrastructure Snapshot

{snapshot}

## Recent Changes

{recent_changes}

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

"""

(DOCS / "aiden-context.md").write_text(output.rstrip() + "\n", encoding="utf-8")
print("Generated docs/aiden-context.md")
