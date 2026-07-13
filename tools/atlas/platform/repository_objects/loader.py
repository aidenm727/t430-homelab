from pathlib import Path

from atlas.platform.repository import repo_root
from atlas.platform.repository_objects.discovery import discover_repository_objects
from atlas.platform.repository_objects.models import (
    RepositoryEntity,
    RepositoryObjectLoadError,
)


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

ParsedYamlValue = str | tuple[str, ...]


def parse_simple_yaml(path: Path) -> dict[str, ParsedYamlValue]:
    values: dict[str, ParsedYamlValue] = {}
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

        if raw_value == "":
            sequence: list[str] = []
            current_item: list[str] = []
            index += 1

            while index < len(lines):
                sequence_line = lines[index]

                if sequence_line and not sequence_line.startswith(" "):
                    break

                stripped = sequence_line.strip()

                if not stripped:
                    index += 1
                    continue

                if stripped.startswith("- "):
                    if current_item:
                        sequence.append(" ".join(current_item))
                    current_item = [stripped[2:].strip()]
                elif current_item:
                    current_item.append(stripped)
                else:
                    raise ValueError(
                        f"Unsupported nested YAML content for field '{key}'."
                    )

                index += 1

            if current_item:
                sequence.append(" ".join(current_item))

            values[key] = tuple(item for item in sequence if item)
            continue

        values[key] = raw_value.strip().strip('"').strip("'")
        index += 1

    return values


def _scalar_value(
    values: dict[str, ParsedYamlValue],
    key: str,
    default: str = "",
) -> str:
    value = values.get(key, default)

    if isinstance(value, tuple):
        return ""

    return value


def _sequence_value(
    values: dict[str, ParsedYamlValue],
    key: str,
) -> tuple[str, ...]:
    value = values.get(key, ())

    if isinstance(value, tuple):
        return tuple(item.strip() for item in value if item.strip())

    text = value.strip()

    if not text:
        return ()

    items: list[str] = []
    current_item: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("- "):
            if current_item:
                items.append(" ".join(current_item))
            current_item = [stripped[2:].strip()]
        elif current_item:
            current_item.append(stripped)
        else:
            return (text,)

    if current_item:
        items.append(" ".join(current_item))

    return tuple(item for item in items if item)


def load_repository_object(
    object_type: str,
    path: Path,
    root: Path | None = None,
) -> RepositoryEntity:
    repository_root = root or repo_root()
    relative_path = str(path.relative_to(repository_root))
    values = parse_simple_yaml(path)

    missing = tuple(
        field for field in REQUIRED_FIELDS if not _scalar_value(values, field)
    )

    return RepositoryEntity(
        path=relative_path,
        object_type=object_type,
        id=_scalar_value(values, "id", "Unknown"),
        title=_scalar_value(values, "title", "Untitled"),
        status=_scalar_value(values, "status", "unknown"),
        capability=_scalar_value(values, "capability", "Unknown"),
        created=_scalar_value(values, "created", "Unknown"),
        source=_scalar_value(values, "source", "Unknown"),
        summary=_scalar_value(values, "summary"),
        rationale=_scalar_value(values, "rationale"),
        evidence=_sequence_value(values, "evidence"),
        notes=_scalar_value(values, "notes"),
        dependencies=_sequence_value(values, "dependencies"),
        related_opportunities=_sequence_value(
            values,
            "related_opportunities",
        ),
        related_documents=_sequence_value(values, "related_documents"),
        missing_fields=missing,
    )


def load_repository_objects(
    object_type: str | None = None,
) -> tuple[list[RepositoryEntity], list[RepositoryObjectLoadError]]:
    entities: list[RepositoryEntity] = []
    errors: list[RepositoryObjectLoadError] = []
    root = repo_root()

    for current_type, path in discover_repository_objects(object_type):
        relative_path = str(path.relative_to(root))

        try:
            entity = load_repository_object(
                current_type,
                path,
                root,
            )
        except Exception as exc:
            errors.append(RepositoryObjectLoadError(relative_path, str(exc)))
            continue

        entities.append(entity)

    return entities, errors
