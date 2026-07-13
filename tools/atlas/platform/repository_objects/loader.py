from pathlib import Path

from atlas.platform.repository import repo_root
from atlas.platform.repository_objects.discovery import discover_repository_objects
from atlas.platform.repository_objects.models import RepositoryEntity, RepositoryObjectLoadError


REQUIRED_FIELDS = (
    "id",
    "title",
    "status",
    "capability",
    "created",
    "source",
    "summary",
    "rationale",
)


def parse_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0

    while index < len(lines):
        line = lines[index]

        if not line.strip():
            index += 1
            continue

        if ":" not in line or line.startswith(" "):
            index += 1
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value in {">", "|"}:
            block: list[str] = []
            index += 1

            while index < len(lines):
                block_line = lines[index]
                if block_line and not block_line.startswith(" "):
                    break
                if block_line.strip():
                    block.append(block_line.strip())
                index += 1

            separator = " " if raw_value == ">" else "\n"
            values[key] = separator.join(block).strip()
            continue

        values[key] = raw_value.strip().strip('"').strip("'")
        index += 1

    return values


def load_repository_objects(object_type: str | None = None) -> tuple[list[RepositoryEntity], list[RepositoryObjectLoadError]]:
    entities: list[RepositoryEntity] = []
    errors: list[RepositoryObjectLoadError] = []
    root = repo_root()

    for current_type, path in discover_repository_objects(object_type):
        relative_path = str(path.relative_to(root))

        try:
            values = parse_simple_yaml(path)
        except Exception as exc:
            errors.append(RepositoryObjectLoadError(relative_path, str(exc)))
            continue

        missing = tuple(field for field in REQUIRED_FIELDS if not values.get(field))

        entities.append(
            RepositoryEntity(
                path=relative_path,
                object_type=current_type,
                id=values.get("id", "Unknown"),
                title=values.get("title", "Untitled"),
                status=values.get("status", "unknown"),
                capability=values.get("capability", "Unknown"),
                created=values.get("created", "Unknown"),
                source=values.get("source", "Unknown"),
                summary=values.get("summary", ""),
                rationale=values.get("rationale", ""),
                evidence=values.get("evidence", ""),
                notes=values.get("notes", ""),
                missing_fields=missing,
            )
        )

    return entities, errors
