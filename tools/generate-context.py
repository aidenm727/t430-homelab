from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

change_session_path = DOCS / "change-session.md"

if change_session_path.exists():
    change_session = change_session_path.read_text(encoding="utf-8")
else:
    change_session = "No active change session found."

mission_path = DOCS / "current-mission.md"

if mission_path.exists():
    mission = mission_path.read_text(encoding="utf-8")
else:
    mission = "Mission document missing."

snapshot_path = DOCS / "infrastructure-snapshot.md"

if snapshot_path.exists():
    snapshot = snapshot_path.read_text(encoding="utf-8")
else:
    snapshot = "Infrastructure snapshot missing."

output = f"""# Aiden Context

Generated: {date.today().isoformat()}

## Purpose

This file is an AI-readable context packet for the homelab project.

It summarizes the current state, active priorities, and operating rules so an AI assistant can quickly understand where the project stands.

## Current Mission

{mission}

## Infrastructure Snapshot

{snapshot}

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