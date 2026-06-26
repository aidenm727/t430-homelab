from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TOOLS = ROOT / "tools"


ARCHITECTURE_DOCS = [
    "docs/architecture/platform.md",
    "docs/architecture/engineering.md",
    "docs/architecture/capabilities.md",
    "docs/architecture/compute.md",
    "docs/architecture/ai.md",
]

CONTEXT_DOCS = [
    "docs/current-mission.md",
    "docs/aiden-context.md",
    "docs/infrastructure-snapshot.md",
]

ROADMAP_DOCS = [
    "docs/roadmaps/ai-engineering.md",
]

TOOL_FILES = [
    "tools/generate-context.py",
    "tools/homelab-change.py",
    "tools/aiden-context-loader.py",
]


def exists(relative_path: str) -> bool:
    return (ROOT / relative_path).exists()


def read_heading(path: Path) -> str:
    if not path.exists():
        return "Missing"

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()

    return path.name


def git_status() -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    except Exception as exc:
        return f"Unable to read git status: {exc}"

    output = result.stdout.strip()
    return output if output else "Clean"


def active_change_session() -> str:
    path = DOCS / "change-session.md"

    if not path.exists():
        return "No change-session.md found."

    text = path.read_text(encoding="utf-8")

    title = "Unknown"
    change_type = "Unknown"

    lines = text.splitlines()

    for index, line in enumerate(lines):
        if line.strip() == "## Change Title" and index + 2 < len(lines):
            title = lines[index + 2].strip()
        if line.strip() == "## Change Type" and index + 2 < len(lines):
            change_type = lines[index + 2].strip()

    return f"{title} ({change_type})"


def recent_changes(limit: int = 5) -> list[str]:
    changes_dir = DOCS / "changes"

    if not changes_dir.exists():
        return ["No structured change records found."]

    records = sorted(
        changes_dir.glob("*.yml"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    return [path.stem for path in records[:limit]] or ["No structured change records found."]


def print_checklist(title: str, files: list[str]) -> None:
    print(f"\n{title}")
    print("-" * len(title))

    for relative in files:
        marker = "✓" if exists(relative) else "✗"
        heading = read_heading(ROOT / relative) if exists(relative) else "Missing"
        print(f"{marker} {relative} — {heading}")


def main() -> None:
    print("# Aiden Platform Engineering State\n")

    print("Git Status")
    print("----------")
    print(git_status())

    print("\nActive Change Session")
    print("---------------------")
    print(active_change_session())

    print("\nRecent Changes")
    print("--------------")
    for change in recent_changes():
        print(f"- {change}")

    print_checklist("Architecture Documents", ARCHITECTURE_DOCS)
    print_checklist("Context Documents", CONTEXT_DOCS)
    print_checklist("Roadmaps", ROADMAP_DOCS)
    print_checklist("Engineering Tools", TOOL_FILES)

    print("\nSuggested Next Step")
    print("-------------------")
    if git_status() != "Clean":
        print("Review and commit or discard current working tree changes.")
    else:
        print("Continue the active change session or finish it with homelab-change.py.")


if __name__ == "__main__":
    main()