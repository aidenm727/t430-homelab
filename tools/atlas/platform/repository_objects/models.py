from dataclasses import dataclass


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
    rationale: str
    evidence: tuple[str, ...] = ()
    notes: str = ""
    dependencies: tuple[str, ...] = ()
    related_opportunities: tuple[str, ...] = ()
    related_documents: tuple[str, ...] = ()
    missing_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class RepositoryObjectLoadError:
    path: str
    message: str
