from pathlib import Path

from atlas.platform.repository import architecture_dir, docs_dir


ARCHITECTURE_SOURCES = [
    "platform.md",
    "engineering.md",
    "capabilities.md",
    "repository.md",
    "atlas.md",
]

INFRASTRUCTURE_SOURCES = [
    "infrastructure.md",
    "infrastructure-gamer-pve.md",
    "services.md",
    "infrastructure-snapshot.md",
]

OPERATIONS_SOURCES = [
    "change-session.md",
    "change-schema.md",
    "changes.log",
]


def existing_files(base: Path, names: list[str]) -> list[Path]:
    return [base / name for name in names if (base / name).exists()]


def architecture_sources() -> list[Path]:
    return existing_files(architecture_dir(), ARCHITECTURE_SOURCES)


def infrastructure_sources() -> list[Path]:
    return existing_files(docs_dir(), INFRASTRUCTURE_SOURCES)


def operations_sources() -> list[Path]:
    return existing_files(docs_dir(), OPERATIONS_SOURCES)


def relative_paths(paths: list[Path]) -> list[str]:
    root = docs_dir().parent
    return [str(path.relative_to(root)) for path in paths]
