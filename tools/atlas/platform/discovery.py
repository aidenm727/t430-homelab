from dataclasses import dataclass
from pathlib import Path

from atlas.platform.document_catalog import Document, DocumentCatalog, make_document
from atlas.platform.repository import architecture_dir, docs_dir, repo_root


@dataclass(frozen=True)
class DocumentLayer:
    name: str
    paths: list[str]


def relative(path: Path) -> str:
    return str(path.relative_to(repo_root()))


def markdown_files(path: Path) -> list[str]:
    if not path.exists():
        return []

    return sorted(
        relative(item)
        for item in path.glob("*.md")
        if item.is_file()
    )


def architecture_documents() -> list[str]:
    return markdown_files(architecture_dir())


def infrastructure_documents() -> list[str]:
    names = [
        "infrastructure.md",
        "infrastructure-virtualization.md",
        "services.md",
        "infrastructure-snapshot.md",
    ]

    return [
        relative(docs_dir() / name)
        for name in names
        if (docs_dir() / name).exists()
    ]


def operations_documents() -> list[str]:
    names = [
        "change-session.md",
        "change-schema.md",
        "changes.log",
        "knowledge-promotion.md",
    ]

    discovered = [
        relative(docs_dir() / name)
        for name in names
        if (docs_dir() / name).exists()
    ]

    changes_dir = docs_dir() / "changes"

    if changes_dir.exists():
        discovered.extend(markdown_files(changes_dir))

    return discovered


def roadmap_documents() -> list[str]:
    return markdown_files(docs_dir() / "roadmaps")


def standards_documents() -> list[str]:
    return markdown_files(docs_dir() / "standards")


def portfolio_evidence_documents() -> list[str]:
    names = [
        "repository-identity-r1-evidence-2026-08-02.md",
    ]

    return [
        relative(docs_dir() / "reviews" / name)
        for name in names
        if (docs_dir() / "reviews" / name).exists()
    ]


def current_context_documents() -> list[str]:
    names = [
        "current-mission.md",
        "aiden-context.md",
        "infrastructure-snapshot.md",
    ]

    return [
        relative(docs_dir() / name)
        for name in names
        if (docs_dir() / name).exists()
    ]


def document_layers() -> list[DocumentLayer]:
    return [
        DocumentLayer("Architecture", architecture_documents()),
        DocumentLayer("Standards", standards_documents()),
        DocumentLayer("Infrastructure", infrastructure_documents()),
        DocumentLayer("Operations", operations_documents()),
        DocumentLayer("Roadmaps", roadmap_documents()),
        DocumentLayer("Portfolio Evidence", portfolio_evidence_documents()),
        DocumentLayer("Current Context", current_context_documents()),
    ]


def document_catalog() -> DocumentCatalog:
    documents: list[Document] = []

    for layer in document_layers():
        for path in layer.paths:
            documents.append(
                make_document(
                    name=path.split("/")[-1],
                    path=path,
                    layer=layer.name,
                )
            )

    return DocumentCatalog(documents)
