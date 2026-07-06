from pathlib import Path

from atlas.platform.repository import repo_root


OBJECT_DIRECTORIES = {
    "engineering-opportunity": "docs/opportunities",
}


def discover_repository_objects(object_type: str | None = None) -> list[tuple[str, Path]]:
    root = repo_root()
    discovered: list[tuple[str, Path]] = []

    directories = OBJECT_DIRECTORIES.items()

    for current_type, relative_dir in directories:
        if object_type is not None and current_type != object_type:
            continue

        base = root / relative_dir
        if not base.exists():
            continue

        for path in sorted(base.rglob("*.yaml")):
            discovered.append((current_type, path))

    return discovered
