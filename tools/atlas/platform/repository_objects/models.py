from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepositoryEntity:
    path: str
    object_type: str
    id: str
    title: str
    status: str
    capability: str
    created: str
    source: str
    summary: str
    missing_fields: tuple[str, ...]


@dataclass(frozen=True)
class RepositoryObjectLoadError:
    path: str
    message: str
