from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "docs/current-mission.md",
    "docs/docs-map.md",
    "docs/architecture/platform.md",
    "docs/architecture/engineering.md",
    "docs/architecture/capabilities.md",
    "docs/architecture/compute.md",
    "docs/architecture/ai.md",
    "docs/roadmaps/ai-engineering.md",
]


def read_file(path: Path) -> str:
    if not path.exists():
        return f"[missing: {path}]"
    return path.read_text(encoding="utf-8")


def main() -> None:
    print("# Aiden Platform Engineering Context\n")

    for relative in FILES:
        path = ROOT / relative
        print(f"\n---\n\n## {relative}\n")
        print(read_file(path).strip())


if __name__ == "__main__":
    main()