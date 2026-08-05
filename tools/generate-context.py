from pathlib import Path
import re

from atlas.platform.active_state import load_active_state
from atlas.platform.reasoning.synchronization import (
    render_generated_context_active_state,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INFRASTRUCTURE_SOURCES = (
    "infrastructure.md",
    "infrastructure-virtualization.md",
    "services.md",
)
STRUCTURED_CHANGE_SOURCE_OWNER = "docs/changes"
STRUCTURED_CHANGE_GLOB = "*.yml"
AIDEN_CONTEXT_GENERATED_FROM = (
    "docs/current-state.json",
    "docs/current-mission.md",
    "docs/infrastructure-snapshot.md",
    STRUCTURED_CHANGE_SOURCE_OWNER,
)


def prepare_embedded_markdown(text: str) -> str:
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


def read_public_source(name: str) -> str:
    path = DOCS / name
    return prepare_embedded_markdown(path.read_text(encoding="utf-8"))


def build_infrastructure_snapshot() -> str:
    sections = []
    for name in INFRASTRUCTURE_SOURCES:
        title = name.removesuffix(".md").replace("-", " ").title()
        sections.append(
            f"## {title}\n\n"
            f"Source: `docs/{name}`\n\n"
            f"{read_public_source(name)}"
        )

    body = "\n\n".join(sections)
    return f"""# Infrastructure Snapshot

> Generated public context artifact.
> Do not edit directly; update the registered canonical infrastructure sources.

This snapshot contains role-based patterns and dated, non-continuous evidence.
It contains no live-state guarantee or exact private operations record.

{body}
"""


def structured_change_paths() -> list[Path]:
    changes_dir = ROOT / STRUCTURED_CHANGE_SOURCE_OWNER
    if not changes_dir.exists():
        return []
    return sorted(changes_dir.glob(STRUCTURED_CHANGE_GLOB))


def load_recent_changes(limit: int = 5) -> list[str]:
    paths = structured_change_paths()
    if not paths:
        return ["No structured change records found."]

    changes: list[tuple[str, str, str]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        date_match = re.search(r"^date:\s*(.+)$", text, re.MULTILINE)
        if title_match and date_match:
            changes.append((date_match.group(1), title_match.group(1), path.name))

    changes.sort(reverse=True)
    return [f"- {change_date} — {title}" for change_date, title, _ in changes[:limit]]


def render_source_graph() -> str:
    lines = []
    for path in AIDEN_CONTEXT_GENERATED_FROM:
        if path == STRUCTURED_CHANGE_SOURCE_OWNER:
            lines.append(f"- {path}/ (`{STRUCTURED_CHANGE_GLOB}` structured records)")
        else:
            lines.append(f"- {path}")
    return "\n".join(lines)


def generate_context() -> None:
    active_state = load_active_state(repository_root=ROOT)
    active_state_projection = render_generated_context_active_state(active_state)

    mission = read_public_source("current-mission.md")

    snapshot_path = DOCS / "infrastructure-snapshot.md"
    snapshot_path.write_text(
        build_infrastructure_snapshot().rstrip() + "\n",
        encoding="utf-8",
    )
    snapshot = prepare_embedded_markdown(snapshot_path.read_text(encoding="utf-8"))
    recent_changes = "\n".join(load_recent_changes())
    source_graph = render_source_graph()
    generated_date = active_state.freshness.effective_date.isoformat()

    output = f"""# Aiden Context

Generated: {generated_date} (canonical-state effective date; deterministic)

## Purpose

This file is an AI-readable generated context packet for the public Aiden
Platform engineering repository. It projects canonical active state, its human
companion, and the registered public-safe infrastructure snapshot. It is
generated and non-canonical.

{active_state_projection}

## Current Mission Companion

{mission}

## Infrastructure Snapshot

{snapshot}

## Recent Changes

{recent_changes}

## Registered Source Graph

{source_graph}

The generated infrastructure snapshot declares its canonical infrastructure
sources. Git history records repository evolution but is not a generator input.

## Use Boundary

- Canonical repository sources win over this generated view.
- Live branch, worktree, infrastructure, and external-system state require fresh observation.
- Task, implementation, publication, deployment, and external-write authority require explicit owner instruction outside repository state.
- Exact private operations, secrets, credentials, and personal School Learning data are excluded.
"""

    (DOCS / "aiden-context.md").write_text(
        output.rstrip() + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    generate_context()
    print("Generated docs/aiden-context.md")
